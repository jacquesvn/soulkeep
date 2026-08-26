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

## Done — "MIDNIGHT" REDESIGN SHIPPED (2026-08-26)
- The Highlord commissioned Claude Design; handoff landed in **docs/design_handoff_wow_roster/**
  (README.md = pixel-final spec; `WoW Roster.dc.html` = working prototype; brief alongside).
- Implemented faithfully as a SPA in **templates/app.html** (old roster.html deleted):
  starfield/nebula + frosted glass + Cinzel/Barlow; Roster grid (summary bar, class-glow cards,
  3 card states, quick-add, 2-click remove); Character Detail (hero, real gear w/ quality colours +
  enchant ✦, M+ tier track + top-3 runs, raid segments, mounts/pets, professions); settings drawer
  (Midnight/Dawn, slumber filter, motion toggle, hourly auto-refresh); sidebar → tab bar <1100px.
- **wowapi.py extended** for detail data (equipment/runs/raid_rows/prof_rows/mounts/pets/avatar/
  last_seen/state). **app.py** now serves JSON: `/api/roster`, `/api/add`, `/api/remove`.
- All verified live in the Browser pane against real API data (Loonwhy/Oblivz/Oblivionn) + mobile.

## Done — EXE BUILT & WINDOW CONFIRMED (2026-08-26, later)
- Sidebar: collapsible (68px icon rail) + **Settings → Sidebar** mode: Static (« button) or
  **Open on hover** (default) — rail flies open OVER the content, no layout shift.
- **WoWRoster.exe** (PyInstaller onefile, ~19MB, --noconsole, eclipse icon.ico): PORTABLE — reads
  `bnet.env` + `roster.json` from the exe's own folder. app.py is frozen-aware (APPDIR vs _MEIPASS
  for templates), picks port 5177 or an ephemeral fallback, waits for Flask before opening the window.
- Smoke-tested the actual exe: window opened, loaded the SPA, fetched the live roster (3 chars).
  **The pywebview window is CONFIRMED working** — the old caveat is closed.
- Build cmd in README. dist/ + build/ + *.spec gitignored (dist holds bnet.env!).

## In flight / NEXT
- Polish: sort options; disk cache for instant first paint. Then Phase 2 (Battle.net login) /
  Phase 4 (Android PWA — design is already fully responsive, a big head start).

See `project_wow_roster` memory + ROADMAP.md + TODO.md.
