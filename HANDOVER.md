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

## In flight / next
- `showcase.py` (find a top active char via M+ leaderboard + full pull) — the US scan returned no
  populated leaderboard (period 1078). Next: try `eu`, or fix the scan, to see rich data before design.
- Then: design data model + dashboard; decide platform (desktop vs web).

See `project_wow_roster` memory + ROADMAP.md + TODO.md.
