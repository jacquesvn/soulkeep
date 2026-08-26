"""Blizzard WoW API fetch + normalize layer for WoW Roster. Stdlib only.
Reads creds from bnet.env / env vars. Caches the OAuth token. get_character() returns a clean,
UI-ready dict (our data model) — the thing the dashboard renders."""
import base64, json, os, sys, time, urllib.error, urllib.parse, urllib.request

_TOKEN = {"value": None, "expires": 0}

CLASS_COLORS = {  # WoW class colours for the UI
    "Warrior": "#C69B6D", "Paladin": "#F48CBA", "Hunter": "#AAD372", "Rogue": "#FFF468",
    "Priest": "#FFFFFF", "Death Knight": "#C41E3A", "Shaman": "#0070DD", "Mage": "#3FC7EB",
    "Warlock": "#8788EE", "Monk": "#00FF98", "Druid": "#FF7C0A", "Demon Hunter": "#A330C9",
    "Evoker": "#33937F",
}

def _creds():
    cid, sec = os.environ.get("BNET_CLIENT_ID"), os.environ.get("BNET_CLIENT_SECRET")
    envf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bnet.env")
    if (not cid or not sec) and os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                if k.strip() == "BNET_CLIENT_ID":     cid = v.strip()
                if k.strip() == "BNET_CLIENT_SECRET":  sec = v.strip()
    if not cid or not sec:
        raise RuntimeError("Missing BNET_CLIENT_ID / BNET_CLIENT_SECRET (set env or bnet.env).")
    return cid, sec

def token():
    if _TOKEN["value"] and time.time() < _TOKEN["expires"] - 60:
        return _TOKEN["value"]
    cid, sec = _creds()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request("https://oauth.battle.net/token", data=data)
    req.add_header("Authorization", "Basic " + base64.b64encode(f"{cid}:{sec}".encode()).decode())
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.load(r)
    _TOKEN["value"], _TOKEN["expires"] = j["access_token"], time.time() + j.get("expires_in", 86400)
    return _TOKEN["value"]

def _get(region, path, namespace):
    q = urllib.parse.urlencode({"namespace": namespace, "locale": "en_US"})
    req = urllib.request.Request(f"https://{region}.api.blizzard.com{path}?{q}")
    req.add_header("Authorization", "Bearer " + token())
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_error": e.code}

def get_character(region, realm, name):
    """Return a normalized character dict, or {'error': ...} if not found/slumbering."""
    region, realm, name = region.lower(), realm.lower(), name.lower()
    ns = f"profile-{region}"
    base = f"/profile/wow/character/{urllib.parse.quote(realm)}/{urllib.parse.quote(name)}"
    p = _get(region, base, ns)
    if p.get("_error"):
        return {"error": p["_error"], "region": region, "realm": realm, "name": name,
                "hint": "slumbering (inactive) or wrong region/realm/name" if p["_error"] == 404 else "api error"}
    mpl   = _get(region, base + "/mythic-keystone-profile", ns)
    raids = _get(region, base + "/encounters/raids", ns)
    profs = _get(region, base + "/professions", ns)
    media = _get(region, base + "/character-media", ns)

    # raid progress -> compact "X/Y H" for the latest instance of the latest expansion
    raid_str, raid_name = "—", None
    exps = raids.get("expansions") or []
    if exps:
        _DRANK = {"Raid Finder": 1, "Normal": 2, "Heroic": 3, "Mythic": 4}
        for inst in reversed((exps[-1].get("instances") or [])):
            modes = inst.get("modes") or []
            if modes:
                # most bosses cleared; on a tie prefer the HIGHER difficulty
                best = max(modes, key=lambda m: (m.get("progress", {}).get("completed_count", 0),
                                                 _DRANK.get(m.get("difficulty", {}).get("name", ""), 0)))
                pr = best.get("progress", {})
                diff = (best.get("difficulty", {}).get("name", "") or "")[:1]  # H/N/M/R
                raid_str = f"{pr.get('completed_count')}/{pr.get('total_count')}{diff}"
                raid_name = inst.get("instance", {}).get("name")
                break

    render = None
    for a in (media.get("assets") or []):
        if a.get("key") in ("main-raw", "main", "avatar"):
            render = a.get("value");
            if a.get("key") == "main-raw": break

    cls = p.get("character_class", {}).get("name")
    return {
        "region": region, "realm_slug": realm,
        "name": p.get("name"), "realm": p.get("realm", {}).get("name"),
        "level": p.get("level"),
        "race": p.get("race", {}).get("name"),
        "class": cls, "class_color": CLASS_COLORS.get(cls, "#BBBBBB"),
        "spec": p.get("active_spec", {}).get("name"),
        "faction": p.get("faction", {}).get("name"),
        "guild": p.get("guild", {}).get("name"),
        "title": p.get("active_title", {}).get("display_string", "").replace("{name}", p.get("name", "")) or None,
        "ilvl": p.get("equipped_item_level"), "ilvl_avg": p.get("average_item_level"),
        "achievement_points": p.get("achievement_points"),
        "last_login": p.get("last_login_timestamp"),
        "mplus_rating": round(mpl.get("current_mythic_rating", {}).get("rating", 0), 1) if not mpl.get("_error") and mpl.get("current_mythic_rating") else None,
        "raid": raid_str, "raid_name": raid_name,
        "professions": [pr.get("profession", {}).get("name") for pr in (profs.get("primaries") or [])] if not profs.get("_error") else [],
        "render": render,
    }

if __name__ == "__main__":  # quick test:  python wowapi.py eu draenor loonwhy
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    c = get_character(*sys.argv[1:4])
    print(json.dumps(c, indent=2, ensure_ascii=False))
