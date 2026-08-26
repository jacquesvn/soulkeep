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

## In flight / NEXT
- Design the data model + roster dashboard from showcase_profile.json (all fields now populated).
- Decide platform (desktop Flask+local vs web) + whether to do Battle.net login/auto-roster.

See `project_wow_roster` memory + ROADMAP.md + TODO.md.
