"""Soulkeep — desktop app (Flask + pywebview). Serves the "Midnight" SPA (templates/app.html),
which pulls live character data from /api/roster. Run:  python app.py  (or the packaged exe)."""
import json, os, secrets, shutil, socket, sys, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

VERSION = "1.3.0"
REPO = "jacquesvn/soulkeep"  # update banner watches this repo's latest release
import webview
from flask import Flask, render_template, request, jsonify, redirect, send_file
import economy
import gamedata
import staticdata
import wowapi

FROZEN = getattr(sys, "frozen", False)
# user data (roster.json, bnet.env) lives next to the exe when packaged — the app is portable
APPDIR = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))
# bundled read-only assets (templates) are unpacked to _MEIPASS by PyInstaller onefile
BUNDLE = getattr(sys, "_MEIPASS", APPDIR)
ROSTER = os.path.join(APPDIR, "roster.json")
CACHE = os.path.join(APPDIR, "roster_cache.json")
app = Flask(__name__, template_folder=os.path.join(BUNDLE, "templates"))
app.config["TEMPLATES_AUTO_RELOAD"] = not FROZEN

def load_roster():
    return json.load(open(ROSTER, encoding="utf-8")) if os.path.exists(ROSTER) else []

def save_roster(r):
    json.dump(r, open(ROSTER, "w", encoding="utf-8"), indent=2)

def key(c):
    return (c["region"].lower(), c["realm"].lower(), c["name"].lower())

def fetch_all(roster):
    if not roster:
        return []
    with ThreadPoolExecutor(max_workers=min(8, len(roster))) as pool:
        return list(pool.map(lambda e: wowapi.get_character(e["region"], e["realm"], e["name"]), roster))

@app.route("/")
def index():
    return render_template("app.html")

@app.route("/api/roster")
def api_roster():
    roster = load_roster()
    if request.args.get("fast"):  # instant paint from the last good fetch, if we have one
        if os.path.exists(CACHE):
            try:
                cached = json.load(open(CACHE, encoding="utf-8"))
                keys = {key(c["entry"]) for c in cached.get("chars", []) if c.get("entry")}
                if keys == {key(e) for e in roster}:  # cache still matches the roster
                    return jsonify({"chars": cached["chars"], "cached": True})
            except (ValueError, KeyError):
                pass
        return jsonify({"chars": None, "cached": False})  # no usable cache — client waits for live
    try:
        chars = fetch_all(roster)
    except RuntimeError:  # bnet.env missing — a fresh install someone was gifted
        return jsonify({"chars": [], "noauth": True})
    for e, c in zip(roster, chars):
        c["entry"] = e  # the region/realm/name key the client sends back for /api/remove
    try:
        json.dump({"chars": chars}, open(CACHE, "w", encoding="utf-8"))
    except OSError:
        pass
    snapshot_history(chars)
    return jsonify({"chars": chars})

# ---------- progress history (the Time Machine's ledger) ----------
HISTORY = os.path.join(APPDIR, "history.jsonl")
HIST_IDX = os.path.join(APPDIR, "history_index.json")

def snapshot_history(chars):
    """Append one compact row per awake character, at most every 6 hours."""
    try:
        idx = json.load(open(HIST_IDX, encoding="utf-8")) if os.path.exists(HIST_IDX) else {}
    except (OSError, ValueError):
        idx = {}
    now = int(time.time())
    gd = gamedata.read_export().get("chars", {})
    rows = []
    for c in chars:
        if c.get("error") or not c.get("name"):
            continue
        k = f"{c['name']}-{c.get('realm')}"
        if now - idx.get(k, 0) < 6 * 3600:
            continue
        g = gd.get(k) or {}
        rows.append({"ts": now, "k": k, "ilvl": c.get("ilvl"), "mplus": c.get("mplus_rating"),
                     "mounts": c.get("mounts"), "pets": c.get("pets"),
                     "ach": c.get("achievement_points"), "gold": g.get("gold")})
        idx[k] = now
    if rows:
        try:
            with open(HISTORY, "a", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            json.dump(idx, open(HIST_IDX, "w", encoding="utf-8"))
        except OSError:
            pass

@app.route("/api/history")
def api_history():
    try:
        rows = [json.loads(x) for x in open(HISTORY, encoding="utf-8")]
    except OSError:
        rows = []
    return jsonify({"rows": rows[-5000:]})

@app.route("/api/realms/<region>")
def api_realms(region):
    return jsonify({"realms": wowapi.get_realms(region)})

@app.route("/api/add", methods=["POST"])
def api_add():
    d = request.get_json(force=True)
    e = {"region": (d.get("region") or "").strip().lower(),
         "realm": (d.get("realm") or "").strip().lower().replace(" ", "-"),
         "name": (d.get("name") or "").strip().lower()}
    if not (e["region"] and e["realm"] and e["name"]):
        return jsonify({"error": "region, realm and name are all required"}), 400
    r = load_roster()
    if any(key(x) == key(e) for x in r):
        return jsonify({"error": "already on the roster"}), 409
    c = wowapi.get_character(e["region"], e["realm"], e["name"])
    r.append(e)
    save_roster(r)
    c["entry"] = e
    return jsonify({"char": c})

@app.route("/api/remove", methods=["POST"])
def api_remove():
    d = request.get_json(force=True)
    e = {"region": d.get("region", ""), "realm": d.get("realm", ""), "name": d.get("name", "")}
    save_roster([c for c in load_roster() if key(c) != key(e)])
    return jsonify({"ok": True})

# ---------- Battle.net login -> auto-roster ----------
AUTH = {"state": None, "region": "eu", "port": 5177}

def _redirect_uri():
    return f"http://localhost:{AUTH['port']}/auth/callback"

@app.route("/auth/login")
def auth_login():
    AUTH["state"] = secrets.token_hex(16)
    AUTH["region"] = (request.args.get("region") or "eu").lower()
    return redirect(wowapi.auth_url(_redirect_uri(), AUTH["state"]))

@app.route("/auth/callback")
def auth_callback():
    if not request.args.get("code") or request.args.get("state") != AUTH["state"]:
        return redirect("/?auth=failed")
    try:
        wowapi.exchange_code(request.args["code"], _redirect_uri())
    except Exception:
        return redirect("/?auth=failed")
    return redirect(f"/?imported={import_account(AUTH['region'])}")

def import_account(region):
    """Pull the account's character list and add anything new (level 10+) to the roster."""
    tok = wowapi.user_token()
    if not tok:
        return 0
    res = wowapi.get_account_chars(region, tok)
    if res.get("_error"):
        return 0
    r = load_roster()
    have = {key(e) for e in r}
    added = 0
    for c in res["chars"]:
        if (c.get("level") or 0) < 10 or not c.get("realm_slug") or not c.get("name"):
            continue
        e = {"region": region, "realm": c["realm_slug"], "name": c["name"].lower()}
        if key(e) not in have:
            r.append(e); have.add(key(e)); added += 1
    if added:
        save_roster(r)
    return added

@app.route("/api/import", methods=["POST"])
def api_import():
    region = (request.get_json(force=True).get("region") or "eu").lower()
    return jsonify({"added": import_account(region)})

def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None

@app.route("/api/account")
def api_account():
    ip = lan_ip()
    return jsonify({"connected": bool(wowapi.user_token()),
                    "redirect_uri": _redirect_uri(),
                    "phone_url": f"http://{ip}:{AUTH['port']}" if ip else None})

# ---------- game data (companion addon SavedVariables) ----------
@app.route("/api/gamedata")
def api_gamedata():
    return jsonify(gamedata.read_export())

@app.route("/api/gamedata/path", methods=["POST"])
def api_gamedata_path():
    ok = gamedata.set_wow_dir(request.get_json(force=True).get("path"))
    return (jsonify({"ok": True}) if ok else (jsonify({"error": "not a directory"}), 400))

@app.route("/api/addon/install", methods=["POST"])
def api_addon_install():
    dst_root = gamedata.addons_dir()
    if not dst_root:
        return jsonify({"error": "WoW folder not found — set it first"}), 400
    src = os.path.join(BUNDLE, "addon", "WoWRosterExport")
    dst = os.path.join(dst_root, "WoWRosterExport")
    try:
        os.makedirs(dst, exist_ok=True)
        for fn in os.listdir(src):
            shutil.copy2(os.path.join(src, fn), os.path.join(dst, fn))
    except OSError as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"ok": True, "installed_to": dst})

# ---------- static game data ----------
@app.route("/api/static/<name>")
def api_static(name):
    if name == "status":
        return jsonify(staticdata.status())
    if name not in ("mounts", "pets", "toys", "journal", "recipes", "season"):
        return jsonify({"error": "unknown"}), 404
    return jsonify({"data": staticdata.load(name)})

@app.route("/api/static/build", methods=["POST"])
def api_static_build():
    staticdata.build_all_async()
    return jsonify({"ok": True})

# ---------- collections / reputations / M+ season ----------
def first_awake():
    for c in (json.load(open(CACHE, encoding="utf-8")).get("chars", []) if os.path.exists(CACHE) else []):
        if not c.get("error"):
            return c
    return None

@app.route("/api/collections")
def api_collections():
    c = first_awake()
    if not c:
        return jsonify({"error": "no awake character"}), 404
    ids = wowapi.get_collection_ids(c["entry"]["region"], c["entry"]["realm"], c["entry"]["name"])
    return jsonify(ids)

@app.route("/api/reputations")
def api_reputations():
    roster = load_roster()
    cached = json.load(open(CACHE, encoding="utf-8")).get("chars", []) if os.path.exists(CACHE) else []
    awake = [c["entry"] for c in cached if not c.get("error")]
    def one(e):
        return {"char": e["name"].capitalize(), "realm": e["realm"],
                "reps": wowapi.get_reputations(e["region"], e["realm"], e["name"])}
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(one, awake))
    return jsonify({"chars": rows})

@app.route("/api/mplus/<region>/<realm>/<name>")
def api_mplus(region, realm, name):
    season = (staticdata.load("season") or {}).get("season_id")
    if not season:
        return jsonify({"error": "season cache not built yet"}), 503
    out = wowapi.get_season_bests(region, realm, name, season)
    out["dungeons"] = (staticdata.load("season") or {}).get("dungeons", [])
    return jsonify(out)

# ---------- economy ----------
@app.route("/api/economy/summary")
def api_econ_summary():
    s = economy.summary()
    return jsonify({"token": economy.token(AUTH["region"]),
                    "ah": {"ts": (s or {}).get("ts"), "count": len((s or {}).get("prices", {})),
                           "refresh": economy.REFRESH},
                    "watches": economy.watches()})

@app.route("/api/economy/refresh", methods=["POST"])
def api_econ_refresh():
    d = request.get_json(force=True, silent=True) or {}
    economy.refresh_ah_async(d.get("region", "eu"), d.get("realm", "draenor"))
    return jsonify({"ok": True})

@app.route("/api/economy/token_history")
def api_token_history():
    return jsonify({"rows": economy.token_history()})

@app.route("/api/economy/search")
def api_econ_search():
    return jsonify({"results": economy.search_item(AUTH["region"], request.args.get("q", ""))})

@app.route("/api/economy/watch", methods=["POST", "DELETE"])
def api_econ_watch():
    d = request.get_json(force=True)
    if request.method == "DELETE":
        return jsonify({"watches": economy.remove_watch(d["id"])})
    return jsonify({"watches": economy.add_watch(d["id"], d.get("name", "?"))})

@app.route("/api/economy/pricehistory")
def api_price_history():
    iid = int(request.args.get("id", 0))
    s = economy.summary()
    cur = {int(k): v for k, v in (s or {}).get("prices", {}).items()}.get(iid)
    return jsonify({"rows": economy.price_history(iid), "current": cur})

@app.route("/api/icon/<int:iid>")
def api_icon(iid):
    url = economy.item_icon(AUTH["region"], iid)
    return redirect(url) if url else (jsonify({"error": "no icon"}), 404)

@app.route("/api/economy/movers")
def api_econ_movers():
    return jsonify({"rows": economy.movers()})

@app.route("/api/economy/profit")
def api_econ_profit():
    cached = json.load(open(CACHE, encoding="utf-8")).get("chars", []) if os.path.exists(CACHE) else []
    crafters = [c for c in cached if not c.get("error") and c.get("professions")]
    def one(c):
        e = c["entry"]
        ids = wowapi.get_known_recipes(e["region"], e["realm"], e["name"])
        return economy.profit_for(ids, c["name"])
    rows = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for group in pool.map(one, crafters):
            rows.extend(group)
    rows.sort(key=lambda r: -r["margin"])
    return jsonify({"rows": rows[:120], "have_ah": bool(economy.summary())})

# ---------- PWA bits (full install needs https hosting; LAN browsing works today) ----------
@app.route("/api/open")
def api_open():
    """Open a page in the user's real browser (whitelisted hosts only)."""
    import webbrowser
    url = request.args.get("url", "")
    allowed = ("https://www.wowhead.com/", f"https://github.com/{REPO}/releases")
    if not url.startswith(allowed):
        return jsonify({"error": "blocked"}), 400
    webbrowser.open(url)
    return jsonify({"ok": True})

# ---------- update check (GitHub Releases) ----------
_VER = {"ts": 0, "latest": None, "url": None}

@app.route("/api/version")
def api_version():
    now = time.time()
    if now - _VER["ts"] > 6 * 3600:
        _VER["ts"] = now  # even on failure, don't hammer GitHub
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest",
                                         headers={"User-Agent": "Soulkeep"})
            with urllib.request.urlopen(req, timeout=10) as r:
                j = json.load(r)
            _VER["latest"] = (j.get("tag_name") or "").lstrip("v")
            _VER["url"] = j.get("html_url")
        except Exception:
            pass
    def tup(v):
        return tuple(int(x) for x in v.split(".") if x.isdigit())
    update = False
    try:
        update = bool(_VER["latest"]) and tup(_VER["latest"]) > tup(VERSION)
    except ValueError:
        pass
    return jsonify({"current": VERSION, "latest": _VER["latest"], "update": update, "url": _VER["url"]})

ZAMCACHE = os.path.join(APPDIR, "zamcache")

@app.route("/zam/<path:path>")
def zam_proxy(path):
    """Same-origin caching proxy for the Wowhead model viewer's assets (their CDN
    blocks third-party origins via CORS; server-side fetch + disk cache keeps us
    same-origin and gentle on their bandwidth)."""
    if ".." in path or path.startswith("/"):
        return jsonify({"error": "bad path"}), 400
    local = os.path.join(ZAMCACHE, path.replace("/", os.sep))
    if not os.path.exists(local):
        try:
            req = urllib.request.Request("https://wow.zamimg.com/modelviewer/live/" + path,
                                         headers={"User-Agent": "Mozilla/5.0 Soulkeep"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            os.makedirs(os.path.dirname(local), exist_ok=True)
            open(local, "wb").write(data)
        except urllib.error.HTTPError as e:
            return jsonify({"error": e.code}), e.code
        except Exception:
            return jsonify({"error": "fetch failed"}), 502
    import mimetypes
    mt = mimetypes.guess_type(local)[0] or ("application/json" if local.endswith(".json") else "application/octet-stream")
    return send_file(local, mimetype=mt)

@app.route("/mv")
def model_viewer():
    return render_template("mv.html")

@app.route("/manifest.webmanifest")
def manifest():
    return jsonify({"name": "Soulkeep", "short_name": "Soulkeep", "start_url": "/",
                    "display": "standalone", "background_color": "#07060E", "theme_color": "#07060E",
                    "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                              {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]})

@app.route("/icon-192.png")
def icon192():
    return send_file(os.path.join(BUNDLE, "icon-192.png"), mimetype="image/png")

@app.route("/icon-512.png")
def icon512():
    return send_file(os.path.join(BUNDLE, "icon-512.png"), mimetype="image/png")

@app.route("/favicon.ico")
def favicon():
    return send_file(os.path.join(BUNDLE, "icon.ico"), mimetype="image/x-icon")

@app.route("/api/qr.png")
def qr_png():
    import io
    import qrcode
    ip = lan_ip()
    if not ip:
        return jsonify({"error": "no LAN address"}), 404
    img = qrcode.make(f"http://{ip}:{AUTH['port']}", box_size=6, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

def pick_port():
    """Prefer 5177 (dev convenience); fall back to an ephemeral port if it's taken."""
    for want in (5177, 0):
        try:
            s = socket.socket()
            s.bind(("127.0.0.1", want))
            port = s.getsockname()[1]
            s.close()
            return port
        except OSError:
            continue
    return 0

if __name__ == "__main__":
    port = pick_port()
    AUTH["port"] = port
    # 0.0.0.0 so a phone on the same WiFi can open the app (Settings shows the URL)
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, threaded=True), daemon=True).start()
    for _ in range(100):  # wait for Flask to come up so the window never opens on a dead page
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                break
        except OSError:
            time.sleep(0.05)
    webview.create_window("Soulkeep", f"http://127.0.0.1:{port}", width=1280, height=880)
    webview.start()
