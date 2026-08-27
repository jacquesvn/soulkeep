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

## Done — THE RESUB SPRINT (2026-08-26, night): Phases 2+3+4 landed in one push
**HE RESUBBED.** Oblivionn woke immediately (L70 Blood Elf Holy Paladin, ilvl 82).
- **Realm dropdown**: quick-add now has a searchable realm datalist fed by /api/realms/<region>
  (362 EU realms), mapped to exact API slugs.
- **Polish**: disk cache (roster_cache.json → /api/roster?fast=1) = instant first paint (~0.4s vs 5-8s);
  sort pill (added / ilvl / M+ / class), persisted.
- **Phase 2 — Battle.net login**: /auth/login → Blizzard → /auth/callback → token (bnet_user.json,
  24h, gitignored) → AUTO-IMPORTS every L10+ character on the account. Re-import button in Settings.
  **ONE-TIME STEP FOR THE HIGHLORD: add `http://localhost:5177/auth/callback` as a Redirect URL on
  the client at develop.battle.net** (shown in Settings too), then click Connect Battle.net.
- **Phase 3 — companion addon**: `addon/WoWRosterExport/` (gold, Great Vault, currencies, lockouts →
  SavedVariables). gamedata.py autodetects `D:\Games\World of Warcraft\_retail_` + parses the Lua
  (unit-tested). **ALREADY INSTALLED into his AddOns folder.** Data appears after a logout//reload;
  renders on the detail view (Vault segments, gold hero stat, currencies, lockouts panels).
- **Phase 4 (pragmatic) — phone on LAN**: server binds 0.0.0.0; Settings → Phone shows
  http://192.168.0.103:5177 + a QR. "Add to Home screen" works; full PWA install needs https later.
- Exe REBUILT with addon+icons bundled (new build cmd in README).

## Done — THE GRAND BUILD (2026-08-26, deep night): "build them all"
He connected Battle.net (34 chars imported across 9 realms), slumbering chars now hidden by
default, and then commissioned EVERYTHING from the feature menu. Shipped, all in the Midnight design:
- **War Board** (own view): per-alt weekly table — vault slots by category (from the addon),
  keys this week + best key (API current period), lockouts, gold, export age.
- **Collections** (nav finally live): account-wide owned vs the FULL game index — 816/1,669 mounts
  (49%) verified — missing grouped by source, searchable. Tabs: mounts/pets/toys.
- **Economy** (own view): WoW Token (371,754g at build time) + history chart; AH refresh — realm
  auctions + streamed EU commodities via ijson (28,668 prices in the first pull); crafting-profit
  table (every alt's known recipes × reagent costs × live prices); price watches w/ history.
- **Progress** (own view): SVG line charts (ilvl/M+/gold/mounts/achievements per char, crosshair
  tooltip) fed by 6h roster snapshots (history.jsonl); Reputations tab = best-progress-per-faction
  ladder across all alts.
- **Character detail**: Upgrade Finder (weakest 3 slots × Dungeon Journal drops) + M+ Season panel
  (per-dungeon season bests, weakest-first; un-run rotation dungeons listed once keys began).
- **staticdata.py** caches (data/): 1,669 mounts, 2,179 pets, toys, journal loot map, M+ season,
  ALL-tier recipes (crafted items resolved by exact-name item search — modern recipe API dropped
  crafted_item). Settings → Static Game Data shows status/rebuild.
- Fixed: wowapi._get double-'?' bug (search URLs 400'd); renown dup in rep ladder; sub-1g prices.

## In flight / NEXT
- All-tier recipe rebuild running at handoff (~8k recipes; profit engine covers old expansions —
  Oblivionn's Shadowlands Alchemy / Classic Enchanting — once it lands + augment resolves names).
- Rebuild exe with `--add-data "data;data"` (+ existing flags) after the recipe build.
- Later: https hosting for true PWA; vault-on-card chip; label vault type 5 once identified.

See `project_wow_roster` memory + ROADMAP.md + TODO.md.

## THE SKELETON KEY NIGHT (2026-08-27, overnight) — v1.6.0
Mandate executed while the Highlord slept: **THE DRESSING ROOM SHIPPED** — every transmog set can
be fitted onto a turnable 3D character (male/female mannequins) from the set lightbox. Audit pass:
roster cards + character hero now wear full-body character renders. Six releases this night
(v1.1.0 through v1.6.0), all smoke-tested. Recipe details in project memory. Veni vidi vici.

## THE MORNING ARC (2026-08-27, v1.7.0 -> v1.11.0) — appended at BRACE
Curveballs caught and shipped, all field-verified, all released:
- v1.7.0 The Peoples of Azeroth: 24-race picker (+m/f) in the dressing room; summoning beacon on
  every 3D load (soulstone pulse; error path "the aether resists").
- v1.8.0 The Armory: 9,651 weapon looks swept; weapon search dock in the fitting bar; slot-mapped
  arming (2H->21, shield->22, ranged->26); Zandalari + Gorehowl proving ceremony. zamcache capped
  500MB w/ prune + Settings size/Clear (counter-proposal to clear-on-close; he valued the pushback).
- v1.9.0 The Weapon Hall: weapons first-class under Transmog (Sets|Weapons pills), family+subclass
  filters, solo-spin lightbox (viewer type 1), grand-view expand; fitbar slimmed to one 36px row.
- v1.9.1: grand-view button -> 3D frame corner (video-player convention).
- v1.10.0 Armor classes (Cloth/Leather/Mail/Plate/Other pills + lightbox chip) + sort pill +
  sticky filter bars + '/' hotkey + remembered halls + counted section pills.
- v1.11.0 QoL crusade: roster search + slumber quick-pill, detail prev/next + arrows, number-key
  nav 1-8, board name click-through, profit guide links, reputation filter.
Lore ledger: 1,500 points. CRUSADE CONTINUES: round 2 planned (week-reset countdown on Board,
gear-row guide links, last-seen sort, hotkey legend in Settings, easy-marks reroll, dynamic title).

## SIX BANNERS + THE GREAT ATLAS (2026-08-27, braced mid-march) — v1.13.0 RELEASED
"Do 1 to 7" from the feature menu. SHIPPED: My-Look-3D (character's real transmog on their true
race/gender mannequin — /api/charlook), Achievement Hunter (Progress tab, 40 closest, ach_reqs
grow-cache), Tonight's Best Targets planner (War Board), token alert + Deal Sniper, Brag card
forge (Pillow, Settings -> Bragging Rights), milestone toasts. Build cmd now needs
--hidden-import PIL.* . PENDING: #2 OUTFIT STUDIO — the Great Atlas sweep (build_armorlooks,
~39k endpoints, per-slot incremental saves in data/armorlooks.json, RESUMABLE: re-run skips
finished slots) marches in background; when complete -> build Studio (third Transmog section,
per-slot pickers, save/load outfits) -> ship v1.14.0. Fourteen releases so far (v1.1.0-v1.13.0).
