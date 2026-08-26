"""WoW Roster — desktop app (Flask + pywebview). Serves the "Midnight" SPA (templates/app.html),
which pulls live character data from /api/roster. Run:  python app.py  (or the packaged exe)."""
import json, os, socket, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
import webview
from flask import Flask, render_template, request, jsonify
import wowapi

FROZEN = getattr(sys, "frozen", False)
# user data (roster.json, bnet.env) lives next to the exe when packaged — the app is portable
APPDIR = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))
# bundled read-only assets (templates) are unpacked to _MEIPASS by PyInstaller onefile
BUNDLE = getattr(sys, "_MEIPASS", APPDIR)
ROSTER = os.path.join(APPDIR, "roster.json")
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
    chars = fetch_all(roster)
    for e, c in zip(roster, chars):
        c["entry"] = e  # the region/realm/name key the client sends back for /api/remove
    return jsonify({"chars": chars})

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
    threading.Thread(target=lambda: app.run(host="127.0.0.1", port=port, threaded=True), daemon=True).start()
    for _ in range(100):  # wait for Flask to come up so the window never opens on a dead page
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                break
        except OSError:
            time.sleep(0.05)
    webview.create_window("WoW Roster", f"http://127.0.0.1:{port}", width=1280, height=880)
    webview.start()
