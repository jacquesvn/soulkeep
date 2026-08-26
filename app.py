"""WoW Roster — desktop app (Flask + pywebview). Renders a roster of characters pulled live from the
Blizzard API via wowapi.py. Run:  python app.py"""
import json, os, threading
from concurrent.futures import ThreadPoolExecutor
import webview
from flask import Flask, render_template, request, redirect, url_for
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

@app.route("/")
def index():
    roster = load_roster()
    # fetch characters concurrently (each is ~5 API calls) so a big roster loads fast; keep order
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(roster)))) as pool:
        chars = list(pool.map(lambda e: wowapi.get_character(e["region"], e["realm"], e["name"]), roster))
    items = [{"entry": e, "char": c} for e, c in zip(roster, chars)]
    return render_template("roster.html", items=items)

@app.route("/add", methods=["POST"])
def add():
    r = load_roster()
    e = {"region": request.form.get("region", "").strip().lower(),
         "realm": request.form.get("realm", "").strip().lower().replace(" ", "-"),
         "name": request.form.get("name", "").strip().lower()}
    if e["region"] and e["realm"] and e["name"] and not any(key(x) == key(e) for x in r):
        r.append(e); save_roster(r)
    return redirect(url_for("index"))

@app.route("/remove", methods=["POST"])
def remove():
    e = {"region": request.form["region"], "realm": request.form["realm"], "name": request.form["name"]}
    save_roster([c for c in load_roster() if key(c) != key(e)])
    return redirect(url_for("index"))

def run_flask():
    app.run(host="127.0.0.1", port=5177, threaded=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    webview.create_window("WoW Roster", "http://127.0.0.1:5177", width=1180, height=860)
    webview.start()
