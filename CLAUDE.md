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

## Tools
- `python spike.py <region> <realm-slug> <name>` — pull one character (works).
- `python showcase.py [region]` — find a top active char via M+ leaderboard + full pull (WIP, see TODO).

See `project_wow_roster` memory for the full picture and the slumbering-account constraint.
