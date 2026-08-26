"""WoW Roster — desktop app (Flask + pywebview). Serves the "Midnight" SPA (templates/app.html),
which pulls live character data from /api/roster. Run:  python app.py"""
import json, os, threading
from concurrent.futures import ThreadPoolExecutor
import webview
from flask import Flask, render_template, request, jsonify
import wowapi

HERE = os.path.dirname(os.path.abspath(__file__))
ROSTER = os.path.join(HERE, "roster.json")
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

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

def run_flask():
    app.run(host="127.0.0.1", port=5177, threaded=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    webview.create_window("WoW Roster", "http://127.0.0.1:5177", width=1280, height=880)
    webview.start()
