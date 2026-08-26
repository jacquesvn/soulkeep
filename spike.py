#!/usr/bin/env python3
"""
Blizzard WoW API spike — pull one character end-to-end so we can see the real JSON
before designing anything. Stdlib only (no pip installs).

Auth: client-credentials OAuth (your registered dev app). Public character data only —
no Battle.net user login needed for this. Credentials come from env vars or bnet.env
(gitignored), NEVER hardcoded/committed.

Run:
    # creds via bnet.env (see bnet.env.example) OR env vars BNET_CLIENT_ID / BNET_CLIENT_SECRET
    python spike.py <region> <realm-slug> <character-name>
    # e.g.  python spike.py us area-52 mycharacter
"""
import base64, json, os, sys, urllib.parse, urllib.request, urllib.error

def load_creds():
    cid = os.environ.get("BNET_CLIENT_ID")
    secret = os.environ.get("BNET_CLIENT_SECRET")
    if (not cid or not secret) and os.path.exists("bnet.env"):
        for line in open("bnet.env", encoding="utf-8"):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                if k.strip() == "BNET_CLIENT_ID":     cid = v.strip()
                if k.strip() == "BNET_CLIENT_SECRET":  secret = v.strip()
    if not cid or not secret:
        sys.exit("Missing BNET_CLIENT_ID / BNET_CLIENT_SECRET (set env vars or bnet.env).")
    return cid, secret

def get_token(cid, secret):
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request("https://oauth.battle.net/token", data=data)
    req.add_header("Authorization", "Basic " + base64.b64encode(f"{cid}:{secret}".encode()).decode())
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["access_token"]

def api_get(region, path, token, namespace):
    params = urllib.parse.urlencode({"namespace": namespace, "locale": "en_US"})
    req = urllib.request.Request(f"https://{region}.api.blizzard.com{path}?{params}")
    req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode(errors="replace")[:300], "_path": path}

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows console is cp1252 by default
    except Exception:
        pass
    if len(sys.argv) != 4:
        sys.exit("usage: python spike.py <region> <realm-slug> <character-name>")
    region, realm, name = sys.argv[1].lower(), sys.argv[2].lower(), sys.argv[3].lower()
    ns = f"profile-{region}"
    cid, secret = load_creds()
    print(f"[auth] getting token for client {cid[:6]}…")
    token = get_token(cid, secret)
    base = f"/profile/wow/character/{urllib.parse.quote(realm)}/{urllib.parse.quote(name)}"

    prof = api_get(region, base, token, ns)
    if prof.get("_error"):
        sys.exit(f"[!] character fetch failed ({prof['_error']}): {prof.get('_body')}\n"
                 f"    Check region/realm-slug/name, and that the character has logged in recently.")
    eq   = api_get(region, base + "/equipment", token, ns)
    mplus= api_get(region, base + "/mythic-keystone-profile", token, ns)
    profs= api_get(region, base + "/professions", token, ns)

    print("\n================= CHARACTER =================")
    cls  = prof.get("character_class", {}).get("name")
    race = prof.get("race", {}).get("name")
    spec = prof.get("active_spec", {}).get("name")
    guild= prof.get("guild", {}).get("name")
    print(f"  {prof.get('name')} — {prof.get('realm',{}).get('name')} ({region.upper()})")
    print(f"  Level {prof.get('level')}  {race} {spec} {cls}  [{prof.get('faction',{}).get('name')}]")
    print(f"  Guild: {guild or '—'}")
    print(f"  Item level: equipped {prof.get('equipped_item_level')} / average {prof.get('average_item_level')}")
    print(f"  Achievement points: {prof.get('achievement_points')}")
    print(f"  Last login (ms epoch): {prof.get('last_login_timestamp')}")

    print("\n----------------- EQUIPMENT ----------------")
    for it in (eq.get("equipped_items") or []):
        slot = it.get("slot", {}).get("name")
        nm   = it.get("name")
        ilvl = it.get("level", {}).get("value")
        qual = it.get("quality", {}).get("name")
        print(f"  {slot:16} ilvl {ilvl:>4}  [{qual}] {nm}")
    if eq.get("_error"): print("  (equipment error:", eq["_error"], ")")

    print("\n----------------- MYTHIC+ ------------------")
    if mplus.get("_error"):
        print("  no M+ data (", mplus["_error"], ") — off-season or none this char")
    else:
        rating = mplus.get("current_mythic_rating", {}).get("rating")
        print(f"  Current season rating: {round(rating,1) if rating else '—'}")
        for run in (mplus.get("current_period", {}).get("best_runs") or [])[:5]:
            dun = run.get("dungeon", {}).get("name"); lvl = run.get("keystone_level")
            print(f"    +{lvl}  {dun}")

    print("\n----------------- PROFESSIONS ---------------")
    for p in (profs.get("primaries") or []):
        prof_name = p.get("profession", {}).get("name")
        tiers = ", ".join(t.get("tier", {}).get("name", "") for t in (p.get("tiers") or []))
        print(f"  {prof_name}: {tiers or '—'}")
    if profs.get("_error"): print("  (professions error:", profs["_error"], ")")

    # dump the raw profile JSON for inspection
    with open("last_profile.json", "w", encoding="utf-8") as f:
        json.dump({"profile": prof, "equipment": eq, "mplus": mplus, "professions": profs}, f, indent=2)
    print("\n[✓] raw JSON written to last_profile.json")

if __name__ == "__main__":
    main()
