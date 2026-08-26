# ROADMAP — WoW Roster

## Phase 0 — Validate the API  ✅ DONE
Dev app registered; client-credentials token + live calls working; `spike.py` pulls a real character
(88KB JSON). Confirmed data surface + gaps (see CLAUDE.md / memory).

## Phase 1 — v1 Roster Dashboard (API-only)  ← NEXT
- Fetch layer: token cache + typed calls for profile/equipment/mplus/professions/collections/raids.
- Data model from real JSON (start from `last_profile.json` / `showcase_profile.json`).
- UI: a roster grid — per character: name, ilvl, spec, M+ rating, raid progress, professions, last-played.
- Add characters by region/realm/name (manual) to start.
- Platform decision: desktop (Flask + local, like the Oblivion/Manager pattern) vs web.

## Phase 2 — Battle.net login → auto-roster
- OAuth authorization-code flow (`wow.profile`), redirect `https://localhost`.
- Account Profile Summary → auto-discover EVERY character, no name-typing. (The "wow" feature.)

## Phase 3 — Weekly chores (needs a companion addon)
- Great Vault, currencies, gold, weekly lockouts — NOT in the REST API.
- Companion addon exports via SavedVariables (desktop app reads it) or copy-paste string.

## Later ideas
Alt gear/upgrade comparison; profession recipe/reagent planning; transmog/mount collection tracking;
"what should I play this week" suggestions; reputation/renown tracking.
