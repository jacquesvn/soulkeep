# ROADMAP — WoW Roster

## Phase 0 — Validate the API  ✅ DONE
Dev app registered; client-credentials token + live calls working; `spike.py` pulls a real character
(88KB JSON). Confirmed data surface + gaps (see CLAUDE.md / memory).

## Phase 1 — v1 Roster Dashboard (API-only)  ✅ BUILT
- [x] Fetch + normalize layer (`wowapi.py`): token cache + `get_character()` → clean UI dict; 404→slumbering.
- [x] Data model from real JSON (Loonwhy → `showcase_profile.json`); expansion=Midnight, cap 90.
- [x] UI (`templates/roster.html`): dark WoW-flavoured grid — name (class-coloured), portrait, ilvl,
      M+ rating, raid progress, professions, title, guild/faction. Slumbering chars show a greyed card.
- [x] Add / remove characters by region/realm/name (manual), stored in `roster.json`.
- [x] Platform: **DESKTOP** — Flask + pywebview window (`app.py`); concurrent per-char fetch.
- Verified end-to-end against Loonwhy (rich), Oblivz (awake/bare), Oblivionn (slumbering card).
- Polish TODO: loading state on first paint; character detail view (gear/collections); refresh button.

## Phase 2 — Battle.net login → auto-roster
- OAuth authorization-code flow (`wow.profile`), redirect `https://localhost`.
- Account Profile Summary → auto-discover EVERY character, no name-typing. (The "wow" feature.)

## Phase 3 — Weekly chores (needs a companion addon)
- Great Vault, currencies, gold, weekly lockouts — NOT in the REST API.
- Companion addon exports via SavedVariables (desktop app reads it) or copy-paste string.

## Later ideas
Alt gear/upgrade comparison; profession recipe/reagent planning; transmog/mount collection tracking;
"what should I play this week" suggestions; reputation/renown tracking.
