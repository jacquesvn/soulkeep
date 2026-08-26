"""One-time builders for game-wide static data: every mount/pet/toy (with sources),
the Dungeon Journal loot map, crafting recipes, and the current M+ season. Cached as
compact JSON under data/ so the app never refetches thousands of endpoints."""
import json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor
import wowapi

HERE = os.path.dirname(os.path.abspath(__file__))
APPDIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else HERE
BUNDLE = getattr(sys, "_MEIPASS", HERE)
DATA = os.path.join(APPDIR, "data")

BUILD = {"running": False, "step": "", "done": 0, "total": 0, "log": []}

def _log(msg):
    BUILD["log"].append(msg)
    print(msg, flush=True)

def load(name):
    """Read a cache file — user-built dir first, then the bundled copy."""
    for base in (DATA, os.path.join(BUNDLE, "data")):
        p = os.path.join(base, name + ".json")
        if os.path.exists(p):
            try:
                return json.load(open(p, encoding="utf-8"))
            except (OSError, ValueError):
                pass
    return None

def _save(name, obj):
    os.makedirs(DATA, exist_ok=True)
    json.dump(obj, open(os.path.join(DATA, name + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))

def _many(items, fn, workers=12):
    """Run fn over items concurrently, tracking BUILD progress; drops failures."""
    BUILD["done"], BUILD["total"] = 0, len(items)
    out = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for r in pool.map(fn, items):
            BUILD["done"] += 1
            if r is not None:
                out.append(r)
    return out

# ---------- collections ----------
def build_mounts(region="eu"):
    BUILD["step"] = "mounts"
    ns = f"static-{region}"
    idx = wowapi._get(region, "/data/wow/mount/index", ns)
    def one(m):
        d = wowapi._get(region, f"/data/wow/mount/{m['id']}", ns)
        if d.get("_error"):
            return None
        return {"id": m["id"], "name": d.get("name") or m.get("name"),
                "src": (d.get("source") or {}).get("name") or "Unknown",
                "faction": (d.get("faction") or {}).get("name")}
    mounts = _many(idx.get("mounts") or [], one)
    _save("mounts", mounts)
    _log(f"mounts: {len(mounts)}")

def build_pets(region="eu"):
    BUILD["step"] = "pets"
    ns = f"static-{region}"
    idx = wowapi._get(region, "/data/wow/pet/index", ns)
    def one(m):
        d = wowapi._get(region, f"/data/wow/pet/{m['id']}", ns)
        if d.get("_error"):
            return None
        return {"id": m["id"], "name": d.get("name") or m.get("name"),
                "src": (d.get("source") or {}).get("name") or "Unknown",
                "type": (d.get("battle_pet_type") or {}).get("name")}
    pets = _many(idx.get("pets") or [], one)
    _save("pets", pets)
    _log(f"pets: {len(pets)}")

def build_toys(region="eu"):
    BUILD["step"] = "toys"
    ns = f"static-{region}"
    idx = wowapi._get(region, "/data/wow/toy/index", ns)
    def one(m):
        d = wowapi._get(region, f"/data/wow/toy/{m['id']}", ns)
        if d.get("_error"):
            return None
        return {"id": m["id"], "name": (d.get("item") or {}).get("name") or m.get("name"),
                "src": d.get("source_description") or (d.get("source") or {}).get("name") or "Unknown"}
    toys = _many(idx.get("toys") or [], one)
    _save("toys", toys)
    _log(f"toys: {len(toys)}")

# ---------- dungeon journal loot ----------
def build_journal(region="eu"):
    BUILD["step"] = "journal"
    ns = f"static-{region}"
    idx = wowapi._get(region, "/data/wow/journal-expansion/index", ns)
    tiers = idx.get("tiers") or []
    picked = [t for t in tiers if t.get("name") == "Current Season"] + tiers[-1:]
    rows, item_ids = [], set()
    for tier in picked:
        exp = wowapi._get(region, f"/data/wow/journal-expansion/{tier['id']}", ns)
        for kind in ("dungeons", "raids"):
            for inst_ref in exp.get(kind) or []:
                inst = wowapi._get(region, f"/data/wow/journal-instance/{inst_ref['id']}", ns)
                if inst.get("_error"):
                    continue
                encs = inst.get("encounters") or []
                def one_enc(e, _inst=inst_ref["name"], _kind=kind):
                    d = wowapi._get(region, f"/data/wow/journal-encounter/{e['id']}", ns)
                    if d.get("_error"):
                        return None
                    return [{"instance": _inst, "kind": _kind[:-1], "boss": d.get("name"),
                             "item_id": (it.get("item") or {}).get("id"),
                             "item": (it.get("item") or {}).get("name")}
                            for it in (d.get("items") or []) if it.get("item")]
                for group in _many(encs, one_enc, workers=8):
                    rows.extend(group)
    # dedupe (Current Season overlaps the expansion list)
    seen, dedup = set(), []
    for r in rows:
        k = (r["instance"], r["boss"], r["item_id"])
        if k not in seen:
            seen.add(k); dedup.append(r); item_ids.add(r["item_id"])
    BUILD["step"] = "journal items"
    def one_item(iid):
        d = wowapi._get(region, f"/data/wow/item/{iid}", ns)
        if d.get("_error"):
            return None
        return (iid, {"slot": (d.get("inventory_type") or {}).get("name"),
                      "quality": (d.get("quality") or {}).get("name"),
                      "cls": (d.get("item_subclass") or {}).get("name")})
    meta = dict(_many(sorted(item_ids), one_item))
    for r in dedup:
        m = meta.get(r["item_id"]) or {}
        r["slot"], r["cls"] = m.get("slot"), m.get("cls")
    dedup = [r for r in dedup if r.get("slot") and r["slot"] != "Non-equippable"]
    _save("journal", dedup)
    _log(f"journal: {len(dedup)} drops")

# ---------- recipes ----------
CRAFTING = {"Alchemy", "Blacksmithing", "Enchanting", "Engineering", "Inscription",
            "Jewelcrafting", "Leatherworking", "Tailoring", "Cooking"}

def build_recipes(region="eu"):
    BUILD["step"] = "recipes"
    ns = f"static-{region}"
    idx = wowapi._get(region, "/data/wow/profession/index", ns)
    out = {}
    for p in idx.get("professions") or []:
        if p.get("name") not in CRAFTING:
            continue
        prof = wowapi._get(region, f"/data/wow/profession/{p['id']}", ns)
        tiers = prof.get("skill_tiers") or []
        recipe_refs = []
        for tier in tiers:  # every expansion tier — alts craft from every era
            td = wowapi._get(region, f"/data/wow/profession/{p['id']}/skill-tier/{tier['id']}", ns)
            recipe_refs += [r for c in (td.get("categories") or []) for r in (c.get("recipes") or [])]
        def one(r, _prof=p["name"]):
            d = wowapi._get(region, f"/data/wow/recipe/{r['id']}", ns)
            if d.get("_error"):
                return None
            crafted = d.get("crafted_item") or d.get("alliance_crafted_item") or {}
            q = d.get("crafted_quantity") or {}
            return (r["id"], {"name": d.get("name"), "prof": _prof,
                              "crafted_id": crafted.get("id"), "crafted": crafted.get("name"),
                              "qty": q.get("value") or q.get("minimum") or 1,
                              "reagents": [{"id": (x.get("reagent") or {}).get("id"),
                                            "name": (x.get("reagent") or {}).get("name"),
                                            "qty": x.get("quantity")} for x in (d.get("reagents") or [])]})
        for rid, rec in _many(recipe_refs, one, workers=12):
            out[str(rid)] = rec
        _log(f"recipes/{p['name']}: {len(recipe_refs)} across {len(tiers)} tiers")
    _save("recipes", out)
    _log(f"recipes: {len(out)} total")

def augment_media(region="eu"):
    """Add artwork URLs to the mount/pet/toy caches (the Hunt's gallery tiles).
    Mounts: creature-display zoom render. Pets: the species icon. Toys: the item icon."""
    ns = f"static-{region}"
    mounts = load("mounts") or []
    BUILD["step"] = "mount art"
    def one_mount(m):
        if m.get("img"):
            return None
        d = wowapi._get(region, f"/data/wow/mount/{m['id']}", ns)
        cds = d.get("creature_displays") or []
        if not cds or not cds[0].get("id"):
            return None
        md = wowapi._get(region, f"/data/wow/media/creature-display/{cds[0]['id']}", ns)
        a = md.get("assets") or []
        return (m["id"], a[0].get("value")) if a else None
    got = dict(x for x in _many(mounts, one_mount) if x)
    for m in mounts:
        if m["id"] in got:
            m["img"] = got[m["id"]]
    _save("mounts", mounts)
    _log(f"mount art: {sum(1 for m in mounts if m.get('img'))}/{len(mounts)}")

    pets = load("pets") or []
    BUILD["step"] = "pet art"
    def one_pet(p):
        if p.get("img"):
            return None
        d = wowapi._get(region, f"/data/wow/pet/{p['id']}", ns)
        return (p["id"], d.get("icon")) if d.get("icon") else None
    got = dict(x for x in _many(pets, one_pet) if x)
    for p in pets:
        if p["id"] in got:
            p["img"] = got[p["id"]]
    _save("pets", pets)
    _log(f"pet art: {sum(1 for p in pets if p.get('img'))}/{len(pets)}")

    toys = load("toys") or []
    BUILD["step"] = "toy art"
    def one_toy(t):
        if t.get("img"):
            return None
        d = wowapi._get(region, f"/data/wow/toy/{t['id']}", ns)
        iid = (d.get("item") or {}).get("id")
        if not iid:
            return None
        md = wowapi._get(region, f"/data/wow/media/item/{iid}", ns)
        a = md.get("assets") or []
        return (t["id"], a[0].get("value")) if a else None
    got = dict(x for x in _many(toys, one_toy) if x)
    for t in toys:
        if t["id"] in got:
            t["img"] = got[t["id"]]
    _save("toys", toys)
    _log(f"toy art: {sum(1 for t in toys if t.get('img'))}/{len(toys)}")

def augment_recipes(region="eu"):
    """Modern recipes (KA/Midnight) dropped crafted_item from the API — resolve the crafted
    item ids by exact-name item search (one id per crafting-quality rank)."""
    BUILD["step"] = "recipe items"
    import urllib.parse
    rec = load("recipes") or {}
    todo = [(rid, r) for rid, r in rec.items() if not r.get("crafted_ids") and not r.get("crafted_id")]
    def one(pair):
        rid, r = pair
        name = r.get("name") or ""
        if not name or name in ("Recraft Equipment", "Sparks"):
            return None
        q = urllib.parse.urlencode({"namespace": f"static-{region}", "name.en_US": name, "_page": 1})
        j = wowapi._get(region, f"/data/wow/search/item?{q}", f"static-{region}")
        ids = []
        for res in (j.get("results") or []):
            d = res.get("data") or {}
            nm = d.get("name")
            nm = nm.get("en_US") if isinstance(nm, dict) else nm
            if nm and nm.lower() == name.lower():
                ids.append(d.get("id"))
        return (rid, ids) if ids else None
    for got in _many(todo, one, workers=10):
        rid, ids = got
        rec[rid]["crafted_ids"] = ids
    _save("recipes", rec)
    n = sum(1 for r in rec.values() if r.get("crafted_ids"))
    _log(f"recipes with crafted item resolved: {n}/{len(rec)}")

def build_season(region="eu"):
    BUILD["step"] = "season"
    dyn = f"dynamic-{region}"
    s = wowapi._get(region, "/data/wow/mythic-keystone/season/index", dyn)
    cur = (s.get("current_season") or {}).get("id")
    d = wowapi._get(region, "/data/wow/mythic-keystone/dungeon/index", dyn)
    _save("season", {"season_id": cur,
                     "dungeons": [{"id": x["id"], "name": x["name"]} for x in (d.get("dungeons") or [])]})
    _log(f"season: id {cur}")

def build_all(region="eu"):
    if BUILD["running"]:
        return
    BUILD.update(running=True, log=[])
    try:
        for fn in (build_season, build_mounts, build_toys, build_journal, build_recipes, augment_recipes, build_pets, augment_media):
            try:
                fn(region)
            except Exception as e:
                _log(f"{fn.__name__} FAILED: {e}")
    finally:
        BUILD.update(running=False, step="done")

def build_all_async(region="eu"):
    threading.Thread(target=build_all, args=(region,), daemon=True).start()

def status():
    return {k: (v[-6:] if k == "log" else v) for k, v in BUILD.items()} | {
        "have": {n: bool(load(n)) for n in ("mounts", "pets", "toys", "journal", "recipes", "season")}}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    build_all(sys.argv[1] if len(sys.argv) > 1 else "eu")
