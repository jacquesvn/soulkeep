# TODO — WoW Roster

## Now
- [x] Fix `showcase.py` — DONE. Scan big realms' current-leaderboard index (not the global dungeon list).
      Pulled Loonwhy@draenor-eu (ilvl 312, M+ 3409, 8/8H Midnight raid, 816 mounts). Rich JSON in showcase_profile.json.
      NOTE: live retail expansion = 'Midnight', level cap 90.
- [ ] Design the data model from real JSON (once we have a rich character).
- [ ] Decide platform: desktop (Flask+local) vs web.

## Soon
- [ ] Build the fetch layer (token cache, typed endpoint calls, error/404 handling).
- [ ] Build the roster grid UI.
- [ ] Manual "add character by region/realm/name".

## Later
- [ ] Battle.net login (OAuth authorization-code, wow.profile) → auto-roster.
- [ ] Weekly-chores companion addon (vault/lockouts/currencies).

## Notes / blockers
- Highlord's own characters SLUMBER (account unsubbed) → they 404 until he resubs + logs in once.
  `Oblivz` (L11 Evoker, Draenor-EU) is awake; `Oblivionn` (his main) sleeps. Dev/test against active chars.
