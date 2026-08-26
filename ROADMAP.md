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

## Phase 1.5 — "Midnight" visual redesign  ✅ SHIPPED
Full Claude Design handoff (docs/design_handoff_wow_roster/) implemented as a single-page app
(`templates/app.html`, replacing roster.html):
- [x] Starfield + nebula ambience, frosted-glass panels, Cinzel/Barlow/Barlow Condensed type.
- [x] Roster view: summary stat bar, class-glow character cards (rich/levelling/slumbering states),
      quick-add (region + "realm / name"), two-click remove, empty + loading states.
- [x] Character Detail view: hero band, full gear list (quality colours + enchant ✦ + per-item ilvl),
      M+ tier track w/ milestone diamonds + top-3 real runs, raid difficulty segment rows,
      mounts/pets counts, profession skill bars. (wowapi.py extended to feed all of it.)
- [x] Settings drawer: account card, Midnight/Dawn themes, show-slumbering filter, ambient-motion
      toggle, hourly auto-refresh + last-sync caption. Settings persist via localStorage.
- [x] Responsive: sidebar → bottom tab bar <1100px; 1-col detail <680px; reduced-motion respected.
- Verified live in-browser: roster + detail render real Loonwhy data; drawer/theme/filters/mobile pass.
- Polish TODO: sort options (ilvl / M+ / class); disk cache for instant first paint.

## Phase 2 — Battle.net login → auto-roster
- OAuth authorization-code flow (`wow.profile`), redirect `https://localhost`.
- Account Profile Summary → auto-discover EVERY character, no name-typing. (The "wow" feature.)

## Phase 3 — Weekly chores (needs a companion addon)
- Great Vault, currencies, gold, weekly lockouts — NOT in the REST API.
- Companion addon exports via SavedVariables (desktop app reads it) or copy-paste string.

## Phase 4 — Android (mobile) — PLANNED
Reuse everything. The Flask backend + `wowapi.py` already do all the work server-side, so the cheapest
real path is the **Lockin pattern**: make `roster.html` responsive, add a PWA manifest + service worker,
and serve it from a hosted Flask instance → installable on Android, no app store.
- KEY: the Blizzard **client_secret stays server-side** (token fetched in Flask, never shipped to the
  phone) — so this needs a hosted backend, not a static github.io page like Lockin was.
- Phase 2 (Battle.net login) matters more here: on mobile you want to log in once and see your roster,
  not type region/realm/name. Do Phase 2 first, then mobile rides on it.
- Alternative (heavier, probably skip): native wrapper (BeeWare/Kivy) or Termux-hosted Flask.

## Phase 5 — Warcraft Logs integration (PLANNED)
WCL has an open GraphQL v2 API (free; client-credentials OAuth, same pattern as Blizzard).
- One-time step for the Highlord: register a client at warcraftlogs.com/api/clients, hand over
  ID+secret (gitignored env file, like bnet.env).
- Unlocks: per-boss parse percentiles in the classic bracket colours (grey->pink), all-star
  points, best performances — a "Performance" panel on the character detail; maybe raid-night
  parse summaries on the War Board. The axis Blizzard's API can't see: not WHAT you killed, but HOW WELL.

## Later ideas
Alt gear/upgrade comparison; profession recipe/reagent planning; transmog/mount collection tracking;
"what should I play this week" suggestions; reputation/renown tracking.
