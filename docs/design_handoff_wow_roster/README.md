# Handoff: WoW Roster — "Midnight" Character Dashboard

## Overview
**WoW Roster** is a desktop-first character-management dashboard for World of Warcraft (retail, *Midnight* expansion, level cap 90). One player's alts are shown at a glance — item level, spec, Mythic+ rating, raid progress, professions, last played — intended to pull live from Blizzard's Battle.net API. Two views: the **Roster** grid (primary) and a **Character Detail** view, plus a slide-out **Settings** drawer. Fully responsive down to phone (sidebar collapses to a bottom tab bar); later ships as an installable PWA / Android app.

## About the Design Files
The files in this bundle are **design references created in HTML** — a working prototype showing the intended look and behavior, not production code to copy directly. The task is to **recreate this design in the target codebase's environment** (React, Vue, native, etc.) using its established patterns — or, if no environment exists yet, pick the most appropriate framework (a React SPA/PWA is the natural fit) and implement the design there.

- `WoW Roster.dc.html` — the full prototype. Markup lives inside `<x-dc>…</x-dc>`; component logic (state + data) is the `class Component` in the `<script data-dc-script>` block. `{{ name }}` holes are bindings filled from `renderVals()`. Everything is inline-styled; the small `<style>` block in `<helmet>` holds only fonts/keyframes/hover rules/media queries.
- `original-design-brief.md` — the original product/design brief; authoritative for intent and sample data.

## Fidelity
**High-fidelity.** Colors, typography, spacing, radii, shadows, animation timings and copy are final. Recreate pixel-perfectly.

---

## Design Tokens

### Core palette (dark "Midnight" theme — CSS custom properties on the app root)
| Token | Value | Use |
|---|---|---|
| `--bg` | `#07060E` | page/void background |
| `--panel` | `#141028` | panel base (used translucently, see Glass) |
| `--raised` | `#1B1636` | raised surface / track fills |
| `--ink` | `#EDE9FF` | primary text (starlight) |
| `--muted` | `#A79FC8` | secondary text |
| `--violet` | `#B15CFF` | primary accent (void corona) |
| `--glow` | `#C77DFF` | accent glow |
| `--deep` | `#7A2FD6` | accent deep (gradient starts) |
| `--gold` | `#F3C766` | Sunwell gold (ilvl, prestige) |
| `--goldhi` | `#E7A93A` | gold deep / warning |
| `--good` | `#6FE0C0` | positive / M+ teal |
| `--warn` | `#E7A93A` | warning |
| `--bad` | `#E0435B` | danger / remove |
| `--line` | `rgba(177,92,255,.14)` | hairlines |
| `--abyss` | `#241A52` | deep shadow/nebula tone |

### Light "Dawn" theme overrides (applied via `data-theme="dawn"` on the root)
`--bg:#F4EFE4; --panel:#FBF7EC; --raised:#FFFFFF; --ink:#241A52; --muted:#6E668F; --violet:#7A2FD6; --glow:#7A2FD6; --gold:#A8751F; --goldhi:#8A5E14; --line:rgba(122,47,214,.18); --starop:0` (starfield hidden via `--starop`).

### Class colours (canonical — players expect these exactly; per-card identity accent)
Warrior `#C69B6D` · Paladin `#F48CBA` · Hunter `#AAD372` · Rogue `#FFF468` · Priest `#FFFFFF` · Shaman `#0070DD` · Warlock `#8788EE` · Monk `#00FF98` · Druid `#FF7C0A` · Demon Hunter `#A330C9` · Evoker `#33937F` · Death Knight `#C41E3A` · Mage `#3FC7EB`.
Each card sets `--cc: <class colour>`; all card glows derive from it.

Faction accents (small dot/tag only, never the card's main colour): Alliance `#4A7FD6`, Horde `#C4232B`.

Item quality colours (gear list): Epic `#A335EE`, Rare `#0070DD`, Legendary `#FF8000`.

### Typography
- **Display**: Cinzel (Google Fonts; 500/600/700) — app wordmark, page titles, character names, raid name, drawer title. Letter-spacing: wordmark `.14em`, `ROSTER` h1 `.12em`, names `.03–.04em`.
- **Body**: Barlow (400/500/600), base 15px.
- **Numerals**: Barlow Condensed (500/600) with `font-variant-numeric: tabular-nums` everywhere numbers align.
- **Eyebrow labels**: 9.5–10.5px, uppercase, letter-spacing `.24em–.32em`, colour `--muted` (violet for section eyebrows).
- Font links: `fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@500;600`.

### Frosted glass recipe (used by every panel)
- Fill: `color-mix(in srgb, var(--panel) 40%, transparent)` (cards: gradient from `color-mix(--raised 52%)` to `color-mix(--panel 38%)` at 58%; sidebar: 55%→30% of `--panel`/`--bg`; settings drawer: 80%→72%).
- `backdrop-filter: blur(14–20px) saturate(1.15)` (+ `-webkit-` prefix). Sidebar 16px, drawer/hero 16–20px, cards/panels 14px.
- Border: `1px solid rgba(237,233,255,.07–.09)`.
- Sheen: top gradient `rgba(237,233,255,.03–.04) → transparent 50–55%` layered over the fill.
- Ambient shadow: `0 8–16px 24–44px -16–28px rgba(0,0,0,.5–.65)`.
- The glass only reads against the background layers (below) — keep them.

### Background layers (behind everything, `pointer-events:none`, opacity `var(--starop)`)
1. **Starfield**: 7 tiny radial-gradient dots (1–2.2px; whites `.5–.75` alpha, violets `.6–.8`, one gold `.5`) tiled at `background-size:600px 600px`, animated `drift 160s linear infinite` (background-position 0 0 → −600px 300px).
2. **Nebula**: four large radial gradients — violet `rgba(177,92,255,.32)` at 78%/−8%, deep violet `.26` at 12%/32%, gold `rgba(243,199,102,.10)` at 96%/62%, abyss `rgba(36,26,82,.85)` at 30%/108%.

### Radii / spacing / misc
- Radii: cards 20px, panels 16–18px, hero 22px, buttons & inputs pill (999px), chips pill, nav items 9px, glow layer matches card 20px.
- Grid gaps: cards 18px, summary 12px, detail columns 18px.
- Main content padding: `34px 40px 28px` desktop; `20px 16px 100px` mobile.
- Scrollbar: 10px, thumb `rgba(177,92,255,.18)` (hover `.35`), pill, transparent track. `::selection` `rgba(177,92,255,.35)`. Input placeholder `rgba(167,159,200,.55)`.
- Links (if any added): `a { color:#C77DFF }`, hover `#F3C766`.
- Focus: `:focus-visible { outline:2px solid #C77DFF; outline-offset:2px; border-radius:4px }`.

### Animations (all under `@media (prefers-reduced-motion: reduce){ *{animation:none!important; transition:none!important} }`)
| Name | Keyframes | Use |
|---|---|---|
| `drift` | background-position 0 0 → −600px 300px, 160s linear infinite | starfield |
| `corona` | box-shadow pulse `0 0 14px 3px rgba(177,92,255,.45)` ↔ `0 0 22px 6px rgba(199,125,255,.6)` (+ matching inset), 6s ease-in-out infinite | eclipse crest, empty-state disc |
| `breathe` | opacity .55 ↔ .8, 5.5s ease-in-out infinite | slumbering cards |
| `cardZoom` | to `scale(1.045)`, opacity 0, `brightness(1.35)`, .26s ease forwards | card exit on click |
| `pageIn` | from `opacity:0; translateY(16px) scale(.985)` → none | entrances (see stagger below) |

**Entrance stagger:** roster header `pageIn .4s cubic-bezier(.25,.8,.3,1)`, summary bar `.45s` +50ms delay, cards `.5s` each delayed `90 + index*45`ms. Detail hero `.4s`, detail grid `.45s` +70ms.

---

## Screens / Views

### 1. App shell
- Root: `height:100vh; overflow:hidden; display:flex`; background `--bg`; both background layers absolutely positioned inside.
- **Sidebar** (desktop ≥1100px): 228px fixed, right hairline border, frosted. Contents top-to-bottom:
  - Crest row (padding `22px 18px 18px`): 26px eclipse disc (radial `#0B0A18 55% → #241A52`, border `rgba(177,92,255,.5)`, `corona` pulse) + wordmark **WoW ROSTER** (Cinzel 700, 15px, `.14em`) with sub-line "MIDNIGHT" (9.5px, `.28em`, muted).
  - Hairline: gradient `transparent → --line 20–80% → transparent`, inset 18px.
  - Nav (10px side padding, 500 weight, muted): Roster ◈, Character ☾, Collections ✦ (inert, 55% opacity), Settings ⛭ (opens drawer). Items: `10px 12px` padding, radius 9px, icon column 16px in `--violet`. Hover: `rgba(177,92,255,.08)` bg + ink text. Active: `rgba(177,92,255,.13)` bg, `inset 2px 0 0 --violet` bar, glow `0 0 24px -4px rgba(177,92,255,.45)`.
  - Footer (auto-pushed): hairline, "EU · Draenor" (12px muted), row of two pill buttons — theme toggle "☾ Midnight"/"☀ Dawn" (hover: violet tint + glow) and ⟳ refresh (hover: rotates 180° over .35s, glows).
- **Bottom tab bar** (<1100px): fixed, `rgba(11,10,24,.92)` + blur(10px), top hairline, safe-area padding. Four buttons (icon 17px above 10px uppercase label): Roster, Character, Collections, Settings. Active = `--glow`, inactive `--muted`.
- **Breakpoints:** `max-width:1100px` — hide sidebar, show tab bar, tighten main padding. `max-width:680px` — header stacks, detail grid & gear list go 1-column. Cards grid uses `repeat(auto-fill, minmax(min(340px,100%),1fr))` so it collapses naturally; **the page body never scrolls horizontally** — only `<main>` scrolls vertically.

### 2. Roster view (default)
- **Header row** (space-between, bottom-aligned): eyebrow `YOUR CHARACTERS · MIDNIGHT` (10.5px, `.32em`, `--violet`) above **ROSTER** — Cinzel 600, 40px, `.12em`, gradient text fill `--ink → rgba(237,233,255,.6)` (background-clip:text). Right: quick-add group — pill container `rgba(237,233,255,.04)` with "EU" segment (12px muted, right hairline) + text input placeholder `Realm / Name` (150px); **+ Add Character** pill — gradient `135deg --deep → --violet`, text `#FBF6FF` 600 13px, border `rgba(199,125,255,.5)`, shadow `0 6px 22px -8px rgba(177,92,255,.7)` + inner top highlight, hover lifts 1px and brightens the glow.
- **Summary bar**: `repeat(auto-fit, minmax(148px,1fr))`, 12px gap. Each stat card: frosted panel, radius 16, `16px 18px` padding; eyebrow label + Barlow Condensed 600 28px number. Values: Characters **8**, Avg Item Level **292** (gold), Top M+ Rating **3610** (teal), Raid-Ready **4**, Achievements **180,412**.
- **Character grid**: cards ≥340px, 18px gap (see Card spec).
- **Empty state** (when roster empty): centered column — 110px eclipse disc with `corona` pulse, "No characters yet" (Cinzel 20px), muted line "Add one above. Only recently-active characters return data."
- **Footer line**: centered, 11px, `.08em`, muted 70%: `Data: Blizzard Battle.net API · retail (Midnight)`.

### 3. Character card (the heart — every detail matters)
Container: frosted gradient glass, radius 20, border `rgba(237,233,255,.09)`, base shadow `0 12px 34px -22px rgba(0,0,0,.6)`, `overflow:hidden`, `transition: transform .22s cubic-bezier(.2,.7,.3,1), box-shadow .22s, border-color .22s`. Sets `--cc` to the class colour. `role="button" tabindex="0"`.

Layers/regions:
1. **Glow layer** (absolute, inset 0, radius 20, pointer-events none): `radial-gradient(130% 95% at 50% 0%, color-mix(in srgb, var(--cc) 14%, transparent), transparent 62%)`; opacity 0 → 1 on card hover (.25s).
2. **Portrait band** (112px, centered): background = class tint `radial-gradient(140% 120% at 50% -10%, <class colour @ 18% alpha (hex+2E)>, transparent 62%)` + 3 star dots. Center: **crest** — 66px circle, border `<class colour hex+55>`, radial class-tint fill, class monogram (initials, e.g. "W", "DH") in Cinzel 700 26px class colour with `text-shadow: 0 0 16px <class colour>`. This is the **portrait slot** — a real character render drops in here later; the crest is the finished fallback. Top-left: `LVL 90` pill (Barlow Condensed 600 11px, `rgba(7,6,14,.45)` bg, hairline border). Top-right: ✕ remove button (24px, opacity .35, hover → opacity 1, `rgba(224,67,91,.15)` bg, `#E0435B`); slumbering cards also show a ☾ mark left of it.
3. **Body** (`14px 16px 12px`, column, 7px gap):
   - Name — Cinzel 600 20px, class colour, `text-shadow: 0 1px 10px rgba(7,6,14,.7)`; optional title beside it, italic 12px `--gold` (e.g. *the Draconic Hero*).
   - Identity line — 12px muted: `Draenor · EU · Lvl 90 Night Elf Destruction Warlock`.
   - Chip row (wrap, 6px gap). Chip: pill, `rgba(237,233,255,.055)` bg, no border, `4px 11px`; tiny uppercase label (8.5px, `.18em`, muted) + value (Barlow Condensed 600 12.5px, tabular). Colours: `ILVL` gold, `M+` teal, `RAID` `#7FE08F`, `LEVEL` warn-gold, professions ink with no label.
   - Levelling cards: 4px XP bar under chips — track `--raised`, fill 62% gradient `--deep → --violet`.
   - Slumbering cards: warning line 12px `--warn`: `⚠ Slumbering — resub & log in once to wake.`
   - Footer row (top hairline `rgba(237,233,255,.06)`, 11.5px muted): guild `‹CMT›` · faction (6px dot in faction colour + name) · right-aligned `Last seen 2 days ago`.

**States:**
- **Rich** (default): everything above.
- **Levelling**: no M+/raid chips; `LEVEL 79 / 90` chip + XP bar; no guild if none.
- **Slumbering**: whole card `filter: saturate(.25) brightness(.78)` + `breathe` pulse; ☾ mark; warning line; **not clickable** (`cursor:default`, no navigation).
- **Hover** (clickable cards): `translateY(-3px)`; border → `color-mix(--cc 32%)`; shadow stack `0 0 0 1px color-mix(--cc 22%)`, `0 18px 44px -18px color-mix(--cc 48%)`, `0 0 52px 2px color-mix(--cc 22%)`, `0 0 110px 16px color-mix(--cc 12%)`; inner glow layer fades in. Subtle but clearly class-coloured.
- **Click**: card plays `cardZoom` (.26s, scale 1.045 + brighten + fade), then detail opens at ~250ms.

### 4. Character Detail view
- **Back button** `← Roster` — muted, hover: ink + `translateX(-3px)`.
- **Hero band** (frosted, radius 22, `30px 32px`, `pageIn` on mount): background overlay = class tint radial at 85%/0% + star dots. Left: 104px crest (as card, 40px monogram, plus halo `0 0 46px -8px <class+66>` and inset glow). Middle: eyebrow `CHARACTER · DRAENOR · EU`, name Cinzel 600 34px class colour + italic gold title, identity line, guild/faction line. Right (auto margin): three headline stats — eyebrows ITEM LEVEL / MYTHIC+ / RAID with Barlow Condensed 600 32px values in gold / teal / `#7FE08F` (em-dash when absent).
- **Content grid** `1.25fr 1fr` (18px gap; 1-col ≤680px), staggered `pageIn`:
  - **Gear panel** (left): eyebrow GEAR; two-column list (1-col ≤680px). Row: slot label (62px col, 9.5px `.14em` uppercase muted) · item name in quality colour (ellipsized) · teal ✦ if enchanted · ilvl (Barlow Condensed 600 13px gold). Rows have bottom hairline `rgba(177,92,255,.07)` and hover highlight `rgba(237,233,255,.045)` (radius 8, .15s). 15 slots: Head, Neck, Shoulders, Back, Chest, Wrists, Hands, Waist, Legs, Feet, Ring ×2, Trinket ×2, Main Hand.
  - **Mythic+ panel**: header row — eyebrow + rating (teal, 24px). **Tier track**: horizontal 2px line (`--raised`), progress fill gradient `--deep → --good` at `rating/3500`; six milestone nodes at 1000/1500/2000/2500/3000/3500 — 11px squares rotated 45° (diamonds), achieved = teal fill/border + `0 0 10px rgba(111,224,192,.5)` glow, unachieved = `--raised`/hairline; value labels under nodes (Barlow Condensed 10px muted). Below: 3 best runs — `+17` (teal, 32px col) + dungeon name + right-aligned score.
  - **Raid panel**: eyebrow RAID; raid name **Sanctum of the Eclipse** (Cinzel 15px); three difficulty rows (Normal/Heroic/Mythic) — uppercase 11px label + `n / 8` right; 8 segments (flex, 3px gap, 7px tall, radius 3): filled = teal (N), gold gradient (H), violet gradient (M); empty = `--raised`.
  - **Collections**: two frosted cards side-by-side — MOUNTS / PETS eyebrows + Barlow Condensed 600 30px counts.
  - **Professions panel**: rows — name (110px) · 5px progress track with gold gradient fill (`skill%`) · `94 / 100` (Barlow Condensed 12px muted).
- Footer line (same as roster).
- Sections hide entirely when the character has no data for them (no M+ panel for the levelling warrior, etc.).

### 5. Settings drawer (slides from the LEFT)
- **Backdrop**: fixed overlay `rgba(7,6,14,.55)` + blur(3px); fades .32s; click closes.
- **Panel**: fixed left, `min(340px, 88vw)`, full height, heavily frosted (blur 20px), right hairline, shadow `24px 0 60px -30px rgba(0,0,0,.7)`. Closed: `translateX(-106%)`; open: `translateX(0)`; transition `.38s cubic-bezier(.32,.9,.3,1)`.
- Header: eyebrow `COMMAND CONSOLE` + **SETTINGS** (Cinzel 19px); ✕ close pill (hover violet tint). Hairline below.
- Sections (scrollable, 22px gaps):
  - **Account**: card with 34px eclipse disc, "Battle.net · EU" 600 13.5px, "Draenor · connected" 11.5px muted, right-aligned teal presence dot with glow.
  - **Appearance**: rows (label 13.5px + 11px muted description, control right): Theme (pill button, same as sidebar toggle) · **Show slumbering characters** (switch) · **Ambient motion** (switch — actually pauses the starfield drift).
  - **Data**: **Auto refresh** switch ("Poll the Battle.net API hourly") + "Last sync · 14 minutes ago" caption.
- **Switch spec**: 40×22px pill; ON = gradient `135deg --deep → --violet`, OFF = `rgba(237,233,255,.12)`; 16px `#EDE9FF` knob, 3px inset, travels 18px, `.25s cubic-bezier(.3,.9,.3,1)`; `role="switch" aria-checked`.
- Footer: `WoW Roster · Midnight · v0.1` caption above nothing else; top hairline.

---

## Interactions & Behavior
- Card click (awake cards only): `cardZoom` on the clicked card → after 250ms navigate to Detail for that character; Detail enters with staggered `pageIn`. Repeat clicks during the transition are ignored.
- Sidebar **Roster/Character** nav and tab bar switch views (Character opens the last-selected character; default first awake character). Active states as specced.
- **Settings** (nav or tab) opens the drawer; backdrop click or ✕ closes.
- ✕ on a card removes the character from the roster (event must not bubble to the card click). In production this should confirm + call the API; prototype just filters it out.
- Theme toggle flips Midnight ↔ Dawn by swapping the token set (`data-theme` attribute). Everything is token-driven; both themes must stay legible.
- "Show slumbering characters" filters slumbering cards out of the grid. "Ambient motion" stops the starfield drift. "Auto refresh" is a visual mock.
- Quick-add input + button are visual mocks (production: region/realm/name lookup → append card).
- Collections nav is intentionally inert (55% opacity) — future surface.
- All hover states listed per component; everything interactive is keyboard-reachable with the violet `:focus-visible` ring.
- `prefers-reduced-motion: reduce` disables all animations and transitions globally.

## State Management
- `view: 'roster' | 'detail'` · `sel: characterName` · `leaving: characterName | null` (click-transition lock) · `theme: 'midnight' | 'dawn'` · `settings: boolean` · `showSlumber: boolean` · `motion: boolean` · `autoRefresh: boolean` · `removed: string[]`.
- Data: one characters array (below) → derive card view-models (chips, identity line, monogram, class colour) and detail view-models (gear list, M+ nodes/runs, raid rows, professions). Summary stats derive from the roster.
- Production data source: Blizzard Battle.net API (profile → characters, equipment, mythic-keystone-profile, raid encounters, professions, collections). Slumbering = API returns 404/no data for an inactive account's character.

## Sample Data (use verbatim)
| # | Name | Race / Class (Spec) | Faction | Realm | Lvl | ilvl | M+ | Raid | Mythic kills | Professions (skill) | Guild | Title | Last seen | State | Mounts | Pets |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Loonwhy | Night Elf Warlock (Destruction) | Alliance | Draenor | 90 | 312 | 3409 | 8/8H | 1 | Enchanting (94) | ‹CMT› | the Draconic Hero | 2 days ago | rich | 214 | 412 |
| 2 | Voidfang | Void Elf Demon Hunter (Havoc) | Alliance | Draenor | 90 | 318 | 3610 | 8/8H | 2 | — | ‹CMT› | Sha'tari Defender | 5 hours ago | rich | 186 | 231 |
| 3 | Sunwarden | Blood Elf Paladin (Retribution) | Horde | Tarren Mill | 90 | 305 | 2740 | 6/8H | 0 | Jewelcrafting (88), Blacksmithing (76) | ‹Eclipse› | the Lightbringer | 1 day ago | rich | 142 | 118 |
| 4 | Emberwing | Dracthyr Evoker (Devastation) | Alliance | Draenor | 90 | 300 | 2510 | 5/8H | 0 | Alchemy (91), Herbalism (100) | ‹CMT› | — | 3 days ago | rich | 97 | 164 |
| 5 | Thornhide | Tauren Druid (Guardian) | Horde | Tarren Mill | 90 | 296 | 2210 | 8/8N | 0 | Leatherworking (82), Skinning (95) | ‹Eclipse› | — | 4 days ago | rich | 121 | 88 |
| 6 | Frostveil | Troll Mage (Frost) | Horde | Tarren Mill | 88 | 284 | 1980 | 3/8N | 0 | Tailoring (64) | ‹Eclipse› | — | 6 days ago | rich | 74 | 59 |
| 7 | Ironhowl | Orc Warrior (Arms) | Horde | Tarren Mill | 79 | 210 | — | — | 0 | Mining (40) | — | — | 1 week ago | levelling | 31 | 12 |
| 8 | Nightwhisper | Night Elf Priest (Shadow) | Alliance | Draenor | 90 | — | — | — | 0 | — | ‹CMT› | — | 47 days ago | slumbering | 0 | 0 |

Raid string semantics: `8/8H` = Normal cleared + 8/8 Heroic; `8/8N` = Normal only. Gear item names in the prototype are procedurally generated flavour ("Voidtouched Crown of the Corona") — production uses real item data; keep the quality-colour + enchant-marker presentation.

## Assets
- **No image assets.** All graphics are CSS: eclipse discs (radial gradient + corona shadow), starfield/nebula (radial gradients), class crests (tinted circle + Cinzel monogram). Icons are text glyphs: ◈ ☾ ✦ ⛭ ⟳ ✕ ⚠ ☀. In production, swap glyphs for the app's icon set and drop real character renders into the portrait band (keep the crest as the loading/error fallback).
- Fonts from Google Fonts (Cinzel, Barlow, Barlow Condensed).

## Files
- `WoW Roster.dc.html` — complete hi-fi prototype (both views, drawer, both themes, all states).
- `original-design-brief.md` — original product brief and art direction.
