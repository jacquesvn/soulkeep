# TODO — WoW Roster

## Now
- [ ] Fix `showcase.py` — US leaderboard scan came back empty (period 1078). Try `python showcase.py eu`,
      or verify current M+ season is live / scan more connected-realms / pick a valid current dungeon+period.
      Goal: see ONE fully-active character's rich data (M+ score, raid, ilvl 600+, collections).
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
