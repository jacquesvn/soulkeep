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

QUALITY_COLORS = {
    "Poor": "#9D9D9D", "Common": "#FFFFFF", "Uncommon": "#1EFF00", "Rare": "#0070DD",
    "Epic": "#A335EE", "Legendary": "#FF8000", "Artifact": "#E6CC80", "Heirloom": "#00CCFF",
}

MAX_LEVEL = 90  # Midnight expansion cap

def _ago(ts_ms):
    """Humanize a last-login timestamp (ms) as 'Last seen ...'."""
    if not ts_ms:
        return None
    mins = max(0, int((time.time() - ts_ms / 1000) / 60))
    if mins < 60:        return f"{mins} minutes ago" if mins != 1 else "1 minute ago"
    hours = mins // 60
    if hours < 24:       return f"{hours} hours ago" if hours != 1 else "1 hour ago"
    days = hours // 24
    if days < 14:        return f"{days} days ago" if days != 1 else "1 day ago"
    weeks = days // 7
    if days < 60:        return f"{weeks} weeks ago"
    return f"{days // 30} months ago"

def _appdir():
    """Next to the exe when frozen (portable app); next to this file when run from source."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _creds():
    cid, sec = os.environ.get("BNET_CLIENT_ID"), os.environ.get("BNET_CLIENT_SECRET")
    envf = os.path.join(_appdir(), "bnet.env")
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

_REALMS = {}  # per-region cache; the realm list changes ~never within a session

def get_realms(region):
    """All realms for a region as [{name, slug}], sorted by name."""
    region = region.lower()
    if region in _REALMS:
        return _REALMS[region]
    j = _get(region, "/data/wow/realm/index", f"dynamic-{region}")
    if j.get("_error"):
        return []
    realms = sorted(({"name": r.get("name"), "slug": r.get("slug")} for r in (j.get("realms") or [])),
                    key=lambda r: r["name"] or "")
    _REALMS[region] = realms
    return realms

def get_character(region, realm, name):
    """Return a normalized character dict (card + detail data), or an error/slumbering stub."""
    region, realm, name = region.lower(), realm.lower(), name.lower()
    ns = f"profile-{region}"
    base = f"/profile/wow/character/{urllib.parse.quote(realm)}/{urllib.parse.quote(name)}"
    p = _get(region, base, ns)
    if p.get("_error"):
        return {"error": p["_error"], "state": "slumbering" if p["_error"] == 404 else "api_error",
                "region": region, "realm_slug": realm, "realm": realm.replace("-", " ").title(),
                "name": name.capitalize(),
                "hint": "Slumbering — resub & log in once to wake." if p["_error"] == 404
                        else f"API error {p['_error']}"}
    mpl    = _get(region, base + "/mythic-keystone-profile", ns)
    raids  = _get(region, base + "/encounters/raids", ns)
    profs  = _get(region, base + "/professions", ns)
    media  = _get(region, base + "/character-media", ns)
    equip  = _get(region, base + "/equipment", ns)
    mounts = _get(region, base + "/collections/mounts", ns)
    pets   = _get(region, base + "/collections/pets", ns)

    # raid progress: compact chip string + per-difficulty rows for the latest instance
    raid_str, raid_name, raid_rows = None, None, []
    exps = raids.get("expansions") or []
    if exps:
        _DRANK = {"Raid Finder": 1, "Normal": 2, "Heroic": 3, "Mythic": 4}
        for inst in reversed((exps[-1].get("instances") or [])):
            modes = inst.get("modes") or []
            if modes:
                # chip: most bosses cleared; on a tie prefer the HIGHER difficulty
                best = max(modes, key=lambda m: (m.get("progress", {}).get("completed_count", 0),
                                                 _DRANK.get(m.get("difficulty", {}).get("name", ""), 0)))
                pr = best.get("progress", {})
                diff = (best.get("difficulty", {}).get("name", "") or "")[:1]  # H/N/M/R
                raid_str = f"{pr.get('completed_count')}/{pr.get('total_count')}{diff}"
                raid_name = inst.get("instance", {}).get("name")
                by_diff = {m.get("difficulty", {}).get("name"): m.get("progress", {}) for m in modes}
                total = next((v.get("total_count") for v in by_diff.values() if v.get("total_count")), 8)
                raid_rows = [{"diff": d, "n": by_diff.get(d, {}).get("completed_count", 0), "total": total}
                             for d in ("Normal", "Heroic", "Mythic")]
                break

    render = avatar = None
    for a in (media.get("assets") or []):
        if a.get("key") == "avatar":   avatar = a.get("value")
        if a.get("key") == "main-raw": render = a.get("value")
        if a.get("key") == "main" and not render: render = a.get("value")

    gear = []
    for it in (equip.get("equipped_items") or []):
        slot = it.get("slot", {}).get("name", "")
        if slot in ("Shirt", "Tabard"):
            continue
        gear.append({"slot": slot, "name": it.get("name"),
                     "ilvl": it.get("level", {}).get("value"),
                     "qcol": QUALITY_COLORS.get(it.get("quality", {}).get("name"), "#FFFFFF"),
                     "ench": bool(it.get("enchantments"))})

    runs = []
    if not mpl.get("_error"):
        best = sorted((mpl.get("current_period", {}).get("best_runs") or []),
                      key=lambda r: -(r.get("mythic_rating", {}).get("rating") or 0))
        runs = [{"key": r.get("keystone_level"), "dungeon": r.get("dungeon", {}).get("name"),
                 "score": round(r.get("mythic_rating", {}).get("rating") or 0, 1)} for r in best[:3]]

    prof_rows = []
    if not profs.get("_error"):
        for pr in (profs.get("primaries") or []):
            tiers = pr.get("tiers") or []
            t = tiers[-1] if tiers else {}
            prof_rows.append({"name": pr.get("profession", {}).get("name"),
                              "skill": t.get("skill_points", 0), "max": t.get("max_skill_points", 100)})

    cls = p.get("character_class", {}).get("name")
    level = p.get("level") or 0
    rating = mpl.get("current_mythic_rating", {}).get("rating") if not mpl.get("_error") else None
    return {
        "region": region, "realm_slug": realm,
        "name": p.get("name"), "realm": p.get("realm", {}).get("name"),
        "level": level, "max_level": MAX_LEVEL,
        "state": "rich" if level >= MAX_LEVEL else "levelling",
        "race": p.get("race", {}).get("name"),
        "class": cls, "class_color": CLASS_COLORS.get(cls, "#BBBBBB"),
        "spec": p.get("active_spec", {}).get("name"),
        "faction": p.get("faction", {}).get("name"),
        "guild": p.get("guild", {}).get("name"),
        "title": p.get("active_title", {}).get("name"),
        "ilvl": p.get("equipped_item_level"), "ilvl_avg": p.get("average_item_level"),
        "achievement_points": p.get("achievement_points"),
        "last_seen": _ago(p.get("last_login_timestamp")),
        "mplus_rating": round(rating) if rating else None,
        "raid": raid_str, "raid_name": raid_name, "raid_rows": raid_rows,
        "professions": [x["name"] for x in prof_rows], "prof_rows": prof_rows,
        "gear": gear, "runs": runs,
        "mounts": len(mounts.get("mounts") or []) if not mounts.get("_error") else None,
        "pets": len(pets.get("pets") or []) if not pets.get("_error") else None,
        "avatar": avatar, "render": render,
    }

if __name__ == "__main__":  # quick test:  python wowapi.py eu draenor loonwhy
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    c = get_character(*sys.argv[1:4])
    print(json.dumps(c, indent=2, ensure_ascii=False))
