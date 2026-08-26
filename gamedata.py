"""Reads the WoWRosterExport addon's SavedVariables — the data the REST API can't give us
(gold, Great Vault, currencies, lockouts). Pure stdlib: a small Lua-table parser tuned to
Blizzard's machine-written SavedVariables format."""
import glob, json, os, re, sys

CANDIDATES = [
    r"D:\Games\World of Warcraft\_retail_",
    r"C:\Program Files (x86)\World of Warcraft\_retail_",
    r"D:\Battle.net\World of Warcraft\_retail_",
    r"D:\World of Warcraft\_retail_",
    r"E:\Games\World of Warcraft\_retail_",
]

def _appdir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _cfgf():
    return os.path.join(_appdir(), "wowdir.json")

def wow_dir():
    """The configured or auto-detected _retail_ dir, or None."""
    try:
        p = json.load(open(_cfgf(), encoding="utf-8")).get("dir")
        if p and os.path.isdir(p):
            return p
    except (OSError, ValueError):
        pass
    for p in CANDIDATES:
        if os.path.isdir(p):
            return p
    return None

def set_wow_dir(path):
    path = (path or "").strip().rstrip("\\/")
    if not os.path.isdir(path):
        return False
    json.dump({"dir": path}, open(_cfgf(), "w", encoding="utf-8"))
    return True

def addons_dir():
    d = wow_dir()
    return os.path.join(d, "Interface", "AddOns") if d else None

# ---------- Lua SavedVariables parser ----------
_TOKEN = re.compile(r'''
    (?P<str>"(?:\\.|[^"\\])*")     |
    (?P<num>-?\d+(?:\.\d+)?(?:e-?\d+)?) |
    (?P<bool>true|false|nil)        |
    (?P<punc>[{}\[\]=,;])
''', re.VERBOSE)

def _tokens(text):
    for m in _TOKEN.finditer(text):
        kind = m.lastgroup
        yield kind, m.group()

def parse_lua_table(text):
    """Parse `Name = { ... }` SavedVariables into a python dict. Tolerant, not a full Lua parser."""
    # Blizzard writes array entries as `value, -- [n]` — strip those trailing index comments
    text = re.sub(r"\s--\s\[\d+\]\s*$", "", text, flags=re.MULTILINE)
    toks = list(_tokens(text[text.index("{"):]))
    pos = 0

    def value():
        nonlocal pos
        kind, tok = toks[pos]
        if kind == "punc" and tok == "{":
            return table()
        pos += 1
        if kind == "str":
            return tok[1:-1].encode().decode("unicode_escape", errors="replace")
        if kind == "num":
            f = float(tok)
            return int(f) if f.is_integer() else f
        if kind == "bool":
            return {"true": True, "false": False, "nil": None}[tok]
        return None

    def table():
        nonlocal pos
        pos += 1  # consume {
        d, arr = {}, []
        while pos < len(toks):
            kind, tok = toks[pos]
            if kind == "punc" and tok == "}":
                pos += 1
                break
            if kind == "punc" and tok in ",;":
                pos += 1
                continue
            if kind == "punc" and tok == "[":  # ["key"] = value  or  [1] = value
                pos += 1
                k = value()
                pos += 2  # consume ] =
                d[k] = value()
            else:
                v = value()
                if pos < len(toks) and toks[pos] == ("punc", "="):
                    pos += 1
                    d[v] = value()
                else:
                    arr.append(v)
        return d if d else arr

    return table()

def read_export():
    """Merge WoWRosterExport SavedVariables across every WoW account on this install.
    Returns {found, wow_dir, chars: {"Name-Realm": {...}}}."""
    d = wow_dir()
    if not d:
        return {"found": False, "wow_dir": None, "chars": {}, "tried": CANDIDATES}
    chars = {}
    files = glob.glob(os.path.join(d, "WTF", "Account", "*", "SavedVariables", "WoWRosterExport.lua"))
    for f in files:
        try:
            data = parse_lua_table(open(f, encoding="utf-8", errors="replace").read())
            if isinstance(data, dict):
                chars.update(data)
        except (OSError, ValueError, IndexError):
            continue
    return {"found": True, "wow_dir": d, "addon_installed": bool(files) or _addon_present(d),
            "has_data": bool(chars), "chars": chars}

def _addon_present(d):
    return os.path.isdir(os.path.join(d, "Interface", "AddOns", "WoWRosterExport"))

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(read_export(), indent=2, ensure_ascii=False)[:2000])
