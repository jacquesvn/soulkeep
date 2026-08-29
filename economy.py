"""Auction-house economy layer: AH price summaries (items + region commodities),
WoW Token tracking, price watches with history, and the crafting profit engine.
The commodity dump is huge (100MB+), so it streams via ijson to a {item: price} map."""
import threading
import gzip, json, os, sys, threading, time, urllib.parse, urllib.request
import staticdata
import wowapi

APPDIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
SUMMARY = os.path.join(APPDIR, "ah_summary.json")
WATCHES = os.path.join(APPDIR, "watches.json")
PRICE_HIST = os.path.join(APPDIR, "price_history.jsonl")
TOKEN_HIST = os.path.join(APPDIR, "token_history.jsonl")

REFRESH = {"running": False, "step": "", "ts": None, "error": None}
_LOCK = threading.Lock()

# ---------- token ----------
def token(region="eu"):
    j = wowapi._get(region, "/data/wow/token/index", f"dynamic-{region}")
    if j.get("_error"):
        return None
    row = {"ts": j.get("last_updated_timestamp"), "price": j.get("price")}
    try:  # append to history once per Blizzard update
        last = None
        if os.path.exists(TOKEN_HIST):
            with open(TOKEN_HIST, "rb") as f:
                lines = f.readlines()
                last = json.loads(lines[-1]) if lines else None
        if not last or last.get("ts") != row["ts"]:
            open(TOKEN_HIST, "a", encoding="utf-8").write(json.dumps(row) + "\n")
    except (OSError, ValueError, IndexError):
        pass
    return row

def token_history(limit=500):
    try:
        return [json.loads(x) for x in open(TOKEN_HIST, encoding="utf-8").readlines()[-limit:]]
    except OSError:
        return []

# ---------- AH fetch ----------
def _stream(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Bearer " + wowapi.token())
    req.add_header("Accept-Encoding", "gzip")
    r = urllib.request.urlopen(req, timeout=300)
    if r.headers.get("Content-Encoding") == "gzip":
        return gzip.GzipFile(fileobj=r)
    return r

def _min_prices_stream(stream, prices):
    """Stream auctions[] and keep the lowest unit price per item id."""
    import ijson
    for a in ijson.items(stream, "auctions.item"):
        iid = (a.get("item") or {}).get("id")
        p = a.get("unit_price") or a.get("buyout")
        q = a.get("quantity") or 1
        if not iid or not p:
            continue
        if a.get("buyout") and not a.get("unit_price") and q > 1:
            p = p // q
        if iid not in prices or p < prices[iid]:
            prices[iid] = p

def connected_realm_id(region, realm_slug):
    r = wowapi._get(region, f"/data/wow/realm/{realm_slug}", f"dynamic-{region}")
    href = ((r.get("connected_realm") or {}).get("href") or "")
    tail = href.rstrip("/").split("/")[-1].split("?")[0]
    return tail if tail.isdigit() else None

def refresh_ah(region="eu", realm_slug="draenor"):
    """Pull realm auctions + region commodities into ah_summary.json. Minutes, run in a thread."""
    with _LOCK:
        if REFRESH["running"]:
            return
        REFRESH.update(running=True, error=None, step="starting")
    try:
        if (region or "").lower() not in {"us", "eu", "kr", "tw", "cn"}:
            raise ValueError(f"bad region {region!r}")
        q = urllib.parse.urlencode({"namespace": f"dynamic-{region}"})
        prices = {}
        REFRESH["step"] = "realm auctions"
        crid = connected_realm_id(region, realm_slug)
        if not crid:
            raise ValueError(f"realm lookup failed for {realm_slug} ({region}) — no prices written")
        _min_prices_stream(_stream(f"https://{region}.api.blizzard.com/data/wow/connected-realm/{crid}/auctions?{q}"), prices)
        REFRESH["step"] = "commodities (large)"
        _min_prices_stream(_stream(f"https://{region}.api.blizzard.com/data/wow/auctions/commodities?{q}"), prices)
        ts = int(time.time())
        json.dump({"ts": ts, "region": region, "realm": realm_slug,
                   "prices": {str(k): v for k, v in prices.items()}},
                  open(SUMMARY, "w", encoding="utf-8"))
        _append_watch_history(ts, prices)
        REFRESH.update(step="done", ts=ts)
    except Exception as e:
        REFRESH["error"] = str(e)
    finally:
        REFRESH["running"] = False

def refresh_ah_async(region="eu", realm_slug="draenor"):
    threading.Thread(target=refresh_ah, args=(region, realm_slug), daemon=True).start()

def summary():
    try:
        return json.load(open(SUMMARY, encoding="utf-8"))
    except (OSError, ValueError):
        return None

# ---------- watches ----------
def watches():
    try:
        return json.load(open(WATCHES, encoding="utf-8"))
    except (OSError, ValueError):
        return []

_WATCH_LOCK = threading.Lock()

def _atomic_dump(obj, path):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def add_watch(item_id, name):
    with _WATCH_LOCK:
        w = watches()
        if not any(x["id"] == item_id for x in w):
            w.append({"id": item_id, "name": name})
            _atomic_dump(w, WATCHES)
    return w

def remove_watch(item_id):
    with _WATCH_LOCK:
        w = [x for x in watches() if x["id"] != item_id]
        _atomic_dump(w, WATCHES)
    return w

def _append_watch_history(ts, prices):
    ids = {x["id"] for x in watches()}
    rec = staticdata.load("recipes") or {}
    for r in rec.values():  # track crafted-item prices too, for the profit engine's history
        for i in (r.get("crafted_ids") or ([r["crafted_id"]] if r.get("crafted_id") else [])):
            ids.add(i)
    rows = [{"ts": ts, "id": i, "p": prices[i]} for i in ids if i in prices]
    if rows:
        with open(PRICE_HIST, "a", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")

def price_history(item_id, limit=300):
    out = []
    try:
        for line in open(PRICE_HIST, encoding="utf-8"):
            r = json.loads(line)
            if r["id"] == item_id:
                out.append(r)
    except OSError:
        pass
    return out[-limit:]

def search_item(region, name):
    q = urllib.parse.urlencode({"namespace": f"static-{region}", "name.en_US": name,
                                "orderby": "id", "_page": 1})
    j = wowapi._get(region, f"/data/wow/search/item?{q}", f"static-{region}")
    out = []
    for r in (j.get("results") or [])[:12]:
        d = r.get("data") or {}
        nm = (d.get("name") or {}).get("en_US") if isinstance(d.get("name"), dict) else d.get("name")
        if nm:
            out.append({"id": d.get("id"), "name": nm,
                        "quality": ((d.get("quality") or {}).get("type") or "").title()})
    return out

# ---------- item icons (grow-as-you-go cache) ----------
ICONS = os.path.join(APPDIR, "item_icons.json")
_ICONS = None

def item_icon(region, iid):
    global _ICONS
    if _ICONS is None:
        try:
            _ICONS = json.load(open(ICONS, encoding="utf-8"))
        except (OSError, ValueError):
            _ICONS = {}
    k = str(iid)
    if k in _ICONS:
        return _ICONS[k]
    md = wowapi._get(region, f"/data/wow/media/item/{iid}", f"static-{region}")
    a = md.get("assets") or []
    url = a[0].get("value") if a else None
    _ICONS[k] = url
    try:
        json.dump(_ICONS, open(ICONS, "w", encoding="utf-8"))
    except OSError:
        pass
    return url

# ---------- market movers (price change between the last two AH refreshes) ----------
def movers(limit=12):
    hist = {}
    try:
        for line in open(PRICE_HIST, encoding="utf-8"):
            r = json.loads(line)
            hist.setdefault(r["id"], []).append((r["ts"], r["p"]))
    except OSError:
        return []
    names = {x["id"]: x["name"] for x in watches()}
    rec = staticdata.load("recipes") or {}
    for r in rec.values():
        ids = r.get("crafted_ids") or ([r["crafted_id"]] if r.get("crafted_id") else [])
        for i in ids:
            names.setdefault(i, r.get("name"))
    out = []
    for iid, rows in hist.items():
        ts = sorted({t for t, _ in rows})
        if len(ts) < 2:
            continue
        by = dict(rows)
        prev, cur = by.get(ts[-2]), by.get(ts[-1])
        if not prev or cur is None:
            continue
        pct = round((cur - prev) / prev * 100, 1)
        if abs(pct) < 0.5:  # a mover has to actually move
            continue
        out.append({"id": iid, "name": names.get(iid) or f"item {iid}",
                    "prev": prev, "cur": cur, "pct": pct})
    out.sort(key=lambda x: -abs(x["pct"]))
    return out[:limit]

# ---------- deal sniper: current price far under historical average ----------
def deals(limit=12, min_samples=3, min_discount=25):
    hist = {}
    try:
        for line in open(PRICE_HIST, encoding="utf-8"):
            r = json.loads(line)
            hist.setdefault(r["id"], []).append((r["ts"], r["p"]))
    except OSError:
        return []
    names = {x["id"]: x["name"] for x in watches()}
    rec = staticdata.load("recipes") or {}
    for r in rec.values():
        ids = r.get("crafted_ids") or ([r["crafted_id"]] if r.get("crafted_id") else [])
        for i in ids:
            names.setdefault(i, r.get("name"))
    out = []
    for iid, rows in hist.items():
        ts = sorted({t for t, _ in rows})
        if len(ts) < min_samples:
            continue
        by = dict(rows)
        cur = by.get(ts[-1])
        past = [by[t] for t in ts[:-1] if by.get(t)]
        if not cur or not past:
            continue
        avg = sum(past) / len(past)
        if avg <= 0:
            continue
        pct = round((avg - cur) / avg * 100, 1)
        if pct >= min_discount:
            out.append({"id": iid, "name": names.get(iid) or f"item {iid}",
                        "cur": cur, "avg": int(avg), "pct": pct})
    out.sort(key=lambda x: -x["pct"])
    return out[:limit]

# ---------- profit engine ----------
def profit_for(known_recipe_ids, char_label, bags=None):
    """Join a character's known recipes against the recipe cache + AH prices.
    bags: optional {item_id: count} across the account — adds 'craftable now'."""
    rec = staticdata.load("recipes") or {}
    s = summary()
    prices = {int(k): v for k, v in (s or {}).get("prices", {}).items()}
    rows = []
    for rid in known_recipe_ids:
        r = rec.get(str(rid))
        if not r:
            continue
        cids = r.get("crafted_ids") or ([r["crafted_id"]] if r.get("crafted_id") else [])
        listed = [prices[i] for i in cids if i in prices]
        if not listed:
            continue  # nothing listed — can't price the craft
        sale = min(listed)  # conservative: cheapest quality rank currently on the AH
        cost, missing = 0, []
        for g in r["reagents"]:
            p = prices.get(g["id"])
            if p is None:
                missing.append(g["name"])
            else:
                cost += p * (g["qty"] or 1)
        qty = r.get("qty") or 1
        craftable = 0
        if bags and r["reagents"]:
            craftable = min((bags.get(g["id"], 0) // max(1, g["qty"] or 1)) for g in r["reagents"])
        rows.append({"char": char_label, "prof": r["prof"], "recipe": r["name"],
                     "crafted_id": cids[0], "sale": sale * qty, "cost": cost,
                     "margin": sale * qty - cost, "missing": missing, "craftable": craftable})
    return rows
