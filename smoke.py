"""Full-app smoke test: hits every API route + static asset and asserts sane shapes.
Usage: python smoke.py [base_url]   (default http://127.0.0.1:5178)"""
import json, sys, urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5178"
PASS, FAIL = [], []

def req(method, path, body=None, raw=False, timeout=90):
    r = urllib.request.Request(BASE + path, method=method,
                               data=json.dumps(body).encode() if body is not None else None,
                               headers={"Content-Type": "application/json"} if body is not None else {})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        data = resp.read()
        return resp.status, (data if raw else json.loads(data))

def check(name, fn):
    try:
        fn()
        PASS.append(name)
        print(f"  PASS  {name}")
    except Exception as e:
        FAIL.append((name, str(e)[:120]))
        print(f"  FAIL  {name}  <- {str(e)[:120]}")

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"smoke vs {BASE}\n")

    check("GET / (SPA shell)", lambda: (lambda s, b: [
        1 / (s == 200), 1 / (b"SOULKEEP" in b), 1 / (b"WAR BOARD" in b.upper())])(*req("GET", "/", raw=True)))
    check("roster fast (cache)", lambda: (lambda s, j: [1 / (s == 200), 1 / ("cached" in j)])(*req("GET", "/api/roster?fast=1")))
    check("roster live", lambda: (lambda s, j: [
        1 / (s == 200), 1 / (len(j["chars"]) >= 2),
        1 / any(c.get("name") == "Oblivionn" for c in j["chars"])])(*req("GET", "/api/roster", timeout=120)))
    check("realms index", lambda: (lambda s, j: [1 / (s == 200), 1 / (len(j["realms"]) > 300)])(*req("GET", "/api/realms/eu")))

    def add_remove():
        s, j = req("POST", "/api/add", {"region": "eu", "realm": "draenor", "name": "smoketestnobody99"})
        assert s == 200 and j["char"]["state"] == "slumbering"
        s2, j2 = req("POST", "/api/remove", {"region": "eu", "realm": "draenor", "name": "smoketestnobody99"})
        assert s2 == 200 and j2["ok"]
        roster = json.load(open("roster.json", encoding="utf-8"))
        assert not any(e["name"] == "smoketestnobody99" for e in roster)
    check("add + remove round-trip", add_remove)

    check("account status", lambda: (lambda s, j: [
        1 / (s == 200), 1 / ("connected" in j), 1 / bool(j["redirect_uri"])])(*req("GET", "/api/account")))
    check("gamedata (addon)", lambda: (lambda s, j: [
        1 / (s == 200), 1 / j["found"], 1 / j["addon_installed"],
        1 / ("Oblivionn-Draenor" in j["chars"])])(*req("GET", "/api/gamedata")))
    check("static status", lambda: (lambda s, j: [
        1 / (s == 200), 1 / j["have"]["mounts"], 1 / j["have"]["journal"]])(*req("GET", "/api/static/status")))
    for name, minlen in (("mounts", 1500), ("pets", 2000), ("toys", 400), ("journal", 300), ("season", 1)):
        check(f"static/{name}", lambda n=name, m=minlen: (lambda s, j: [
            1 / (s == 200), 1 / (len(j["data"]) >= m if n != "season" else bool(j["data"]["season_id"]))])(*req("GET", f"/api/static/{n}")))
    check("collections (account)", lambda: (lambda s, j: [
        1 / (s == 200), 1 / (50 < len(j["mounts"]) < 500), 1 / (len(j["toys"]) > 20)])(*req("GET", "/api/collections")))
    check("reputations ladder", lambda: (lambda s, j: [
        1 / (s == 200), 1 / (len(j["chars"]) >= 2),
        1 / any(cr["reps"] for cr in j["chars"])])(*req("GET", "/api/reputations", timeout=120)))
    check("mplus season", lambda: (lambda s, j: [
        1 / (s == 200), 1 / ("runs" in j), 1 / (len(j["dungeons"]) > 5)])(*req("GET", "/api/mplus/eu/draenor/oblivionn")))
    check("history rows", lambda: (lambda s, j: [
        1 / (s == 200), 1 / (len(j["rows"]) >= 2)])(*req("GET", "/api/history")))

    check("economy summary", lambda: (lambda s, j: [
        1 / (s == 200), 1 / (j["token"]["price"] > 0), 1 / (j["ah"]["count"] > 10000)])(*req("GET", "/api/economy/summary")))
    check("token history", lambda: (lambda s, j: [
        1 / (s == 200), 1 / (len(j["rows"]) >= 1)])(*req("GET", "/api/economy/token_history")))
    check("item search", lambda: (lambda s, j: [
        1 / (s == 200), 1 / any("Flux" in r["name"] for r in j["results"])])(*req("GET", "/api/economy/search?q=Weak%20Flux")))

    def watch_cycle():
        s, j = req("POST", "/api/economy/watch", {"id": 2880, "name": "Weak Flux"})
        assert any(w["id"] == 2880 for w in j["watches"])
        s2, j2 = req("GET", "/api/economy/pricehistory?id=2880")
        assert s2 == 200 and "current" in j2
        s3, j3 = req("DELETE", "/api/economy/watch", {"id": 2880})
        assert not any(w["id"] == 2880 for w in j3["watches"])
    check("watch add/price/remove", watch_cycle)

    for path, ctype in (("/manifest.webmanifest", b"Soulkeep"), ("/icon-192.png", b"PNG"),
                        ("/icon-512.png", b"PNG"), ("/favicon.ico", b""), ("/api/qr.png", b"PNG")):
        check(f"asset {path}", lambda p=path, c=ctype: (lambda s, b: [
            1 / (s == 200), 1 / (c in b[:2000] if c else len(b) > 500)])(*req("GET", p, raw=True)))

    print(f"\n===== {len(PASS)} passed, {len(FAIL)} failed =====")
    for n, e in FAIL:
        print(f"  FAILED: {n}: {e}")
    sys.exit(1 if FAIL else 0)

if __name__ == "__main__":
    main()
