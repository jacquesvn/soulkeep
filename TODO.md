# TODO — WoW Roster

## Done (v1 desktop app)
- [x] Fix `showcase.py` — scan big realms' current-leaderboard index. Pulled Loonwhy@draenor-eu.
- [x] Design the data model from real JSON → `wowapi.get_character()` normalized dict.
- [x] Platform decided: **DESKTOP** (Flask + pywebview).
- [x] Fetch layer (`wowapi.py`): token cache, typed calls, 404/slumbering handling.
- [x] Roster grid UI (`templates/roster.html`) + concurrent fetch (`app.py`).
- [x] Add/remove character by region/realm/name (`roster.json`).
- [x] Verified end-to-end (rich / awake-bare / slumbering cards all render).

## Next (v1 polish)
- [ ] Loading state on first paint (first load fires ~5 API calls/char — a few seconds of blank).
- [ ] Manual "Refresh" button (re-fetch without editing the roster).
- [ ] Character detail view: full gear (ilvl/quality/gems/enchants), mounts/pets counts, best M+ runs.
      (showcase.py already pulls all of this; the data is there — just needs a route + template.)
- [ ] Sort/group the grid (by ilvl, class, realm).
- [ ] Cache the last good fetch to disk so the window paints instantly, then refreshes.

## Later
- [ ] Battle.net login (OAuth authorization-code, `wow.profile`) → auto-roster (Phase 2, the "wow" feature).
- [ ] Weekly-chores companion addon (vault/lockouts/currencies) → SavedVariables/export (Phase 3).

## Notes / blockers
- Highlord's own characters SLUMBER (account unsubbed) → 404 until he resubs + logs in once.
  `Oblivz` (L11 Evoker, Draenor-EU) is awake; `Oblivionn` (his main) sleeps (shows a greyed card).
  Seed roster ships with Loonwhy (rich demo) + Oblivz + Oblivionn so the app looks alive on first run.
