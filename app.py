"""WoW Roster — desktop app (Flask + pywebview). Serves the "Midnight" SPA (templates/app.html),
which pulls live character data from /api/roster. Run:  python app.py  (or the packaged exe)."""
import json, os, secrets, shutil, socket, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
import webview
from flask import Flask, render_template, request, jsonify, redirect, send_file
import gamedata
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
    chars = fetch_all(roster)
    for e, c in zip(roster, chars):
        c["entry"] = e  # the region/realm/name key the client sends back for /api/remove
    try:
        json.dump({"chars": chars}, open(CACHE, "w", encoding="utf-8"))
    except OSError:
        pass
    return jsonify({"chars": chars})

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

# ---------- PWA bits (full install needs https hosting; LAN browsing works today) ----------
@app.route("/manifest.webmanifest")
def manifest():
    return jsonify({"name": "WoW Roster", "short_name": "WoW Roster", "start_url": "/",
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
    webview.create_window("WoW Roster", f"http://127.0.0.1:{port}", width=1280, height=880)
    webview.start()
