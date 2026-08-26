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

## The app (v1 — BUILT)
Desktop app: **Flask backend + pywebview window**, stdlib-only API layer.
- `wowapi.py` — fetch + normalize. `get_character(region, realm, name)` → a clean UI-ready dict
  (name/class/spec/ilvl/M+ rating/raid/professions/title/render/class_color), or `{error, hint}` on
  404 (slumbering). Caches the OAuth token; reads creds from `bnet.env`.
- `app.py` — Flask routes (`/`, `/add`, `/remove`) + the pywebview desktop window. Fetches the roster
  **concurrently** (ThreadPoolExecutor). Run it: `python app.py`.
- `templates/roster.html` — dark WoW-flavoured roster grid; class-coloured names, portraits, stat chips.
- `roster.json` — the tracked characters (region/realm/name), edited live via the add/remove UI.

## Dev scripts (kept for reference)
- `python spike.py <region> <realm-slug> <name>` — pull one raw character → last_profile.json.
- `python showcase.py [region]` — find a top active char via M+ leaderboard + full pull → showcase_profile.json
  (the data-model reference).
- `python wowapi.py <region> <realm> <name>` — print the normalized dict for one character.

See `project_wow_roster` memory for the full picture and the slumbering-account constraint.
