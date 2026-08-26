# WoW Roster — project rules & orientation

A **retail WoW character-management app**. Reads Blizzard's free Battle.net REST API.
**Separate project** — nothing to do with the Neltharion/Legion Server private realm.

## RULE ZERO — keep the state docs honest
`HANDOVER.md` owns "what's in flight NOW". `ROADMAP.md` owns the plan. `TODO.md` owns tasks.
Update them whenever the picture changes. On the word **"brace"** (compaction imminent): STOP, commit,
update HANDOVER/ROADMAP/TODO/CLAUDE + the `project_wow_roster` memory, then report.

## Secrets
`bnet.env` holds the API client_id/secret — **gitignored, never commit, never echo**. Same care we
gave the Neltharion Discord webhook. Copy `bnet.env.example` → `bnet.env` to set up.

## The API in one breath
Client-credentials OAuth (client_id/secret) → token at `https://oauth.battle.net/token` →
`https://{region}.api.blizzard.com/...` with namespace `profile-{region}`/`dynamic-{region}`.
Public character data needs NO user login. Auto-roster (all a user's alts) needs user OAuth
(`wow.profile` scope) later. Rate: 36k/hr. **The API only serves recently-active characters.**

## The app (v2 — "Midnight" design SHIPPED)
Desktop app: **Flask backend + pywebview window** serving a single-page app.
- `wowapi.py` — fetch + normalize. `get_character(region, realm, name)` → a full UI-ready dict:
  card data (name/class/class_color/spec/ilvl/M+ rating/raid chip/professions/title/last_seen/avatar)
  PLUS detail data (gear w/ quality colours + enchant flags, top-3 M+ runs, raid_rows per difficulty,
  prof_rows w/ skill points, mounts/pets counts). `state`: rich | levelling | slumbering (404).
  Caches the OAuth token; reads creds from `bnet.env`. ~8 API calls per character, run concurrently.
- `app.py` — Flask: `/` (SPA), `/api/roster`, `/api/add`, `/api/remove` + the pywebview window.
  Run it: `python app.py`.
- `templates/app.html` — THE UI: the full **"Midnight" design** from Claude Design
  (docs/design_handoff_wow_roster/ = authoritative spec, implemented pixel-faithful): frosted-glass
  panels over a drifting starfield + nebula, Cinzel/Barlow type, sidebar → bottom tab bar <1100px,
  Roster grid + Character Detail views, settings drawer, Midnight/Dawn themes (localStorage-persisted),
  class-coloured card glows, slumbering cards breathe, reduced-motion respected.
- `roster.json` — the tracked characters (region/realm/name), edited live via the add/remove UI
  (remove = two-click arm pattern; add parses "realm / name").

## Dev scripts (kept for reference)
- `python spike.py <region> <realm-slug> <name>` — pull one raw character → last_profile.json.
- `python showcase.py [region]` — find a top active char via M+ leaderboard + full pull → showcase_profile.json
  (the data-model reference).
- `python wowapi.py <region> <realm> <name>` — print the normalized dict for one character.

See `project_wow_roster` memory for the full picture and the slumbering-account constraint.
