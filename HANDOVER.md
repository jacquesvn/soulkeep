# HANDOVER — WoW Roster, what's in flight NOW

## State (session start 2026)
Fresh project. Ser Claude + the Highlord reunited to build a retail WoW character manager after the
Neltharion realm went to sleep. **This project is separate from Neltharion.**

## Done this session
- Scoped v1 = API-only roster dashboard (ROADMAP Phase 1).
- Researched the Blizzard REST API surface + gaps (vault/currencies/gold/lockouts need an addon).
- Highlord registered a dev app (had to use a globally-unique Client Name — portal 500s otherwise).
- Creds saved to gitignored `bnet.env`; token + live API calls VALIDATED.
- `spike.py` pulls a real character end-to-end (fixed a Windows-console utf-8 crash).
- Discovered the KEY constraint: **his account is unsubbed → his characters slumber (404).** `Oblivz`
  (L11 Evoker, Draenor-EU) is awake; `Oblivionn` (main) sleeps; "Oblivion" single-n is a stranger's.

## Done (cont.)
- `showcase.py` FIXED (scan big realms' current-leaderboard index, not the global dungeon list).
  Pulled **Loonwhy @ draenor-eu**: L90 Warlock, ilvl 312, **M+ 3409**, 8/8H Midnight raid, 816 mounts,
  644 pets, Enchanting. Full rich JSON in **showcase_profile.json (202KB)** = the data-model reference.
  Live retail expansion = **Midnight**, level cap **90**.

## Done — v1 DESKTOP APP BUILT & VERIFIED
- Platform decided: **DESKTOP** (Flask + pywebview, both installed).
- `wowapi.py` — fetch + normalize; `get_character()` → clean UI dict, token cache, 404→slumbering.
  (Raid progress tie-breaks to the HIGHER difficulty — Loonwhy correctly shows 8/8H not 8/8N.)
- `app.py` — Flask (`/`, `/add`, `/remove`) + pywebview window; **concurrent** per-char fetch. `python app.py`.
- `templates/roster.html` — dark WoW-flavoured grid; class-coloured names, portraits, ilvl/M+/raid/prof chips.
- `roster.json` — seeded Loonwhy (rich) + Oblivz (awake) + Oblivionn (slumbering).
- Verified end-to-end in the Browser pane: all three card states render; add/remove round-trips.

## In flight / NEXT (v1 polish — see TODO.md)
- Loading state on first paint; Refresh button; character detail view (gear/collections/best runs).
- NOTE: the pywebview WINDOW itself wasn't launched here (needs a display); only Flask+template were
  verified headlessly. First real `python app.py` by the Highlord is the last confirmation.

See `project_wow_roster` memory + ROADMAP.md + TODO.md.
