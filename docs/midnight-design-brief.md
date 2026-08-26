# Design brief — "WoW Roster", themed for the *Midnight* expansion

> Paste everything below the line into Claude design. It is a complete brief: the product, the exact
> data each card shows, every screen and state, the full art direction, sample content to populate it,
> and the technical constraints of a self-contained page.

---

## What you're designing

**WoW Roster** — a desktop-first character-management dashboard for *World of Warcraft* (retail, current
expansion **Midnight**, level cap **90**). One player has many characters ("alts") across the game; this
app shows them all at a glance — item level, spec, Mythic+ rating, raid progress, professions, last
played — pulled live from Blizzard's API. Think "command console for my whole roster." It is used by an
enthusiast player who alt-hops constantly and wants to see, in one beautiful screen, where every
character stands.

Deliver a **single self-contained HTML page** (inline CSS + JS, no build step) that is a polished,
production-quality mockup of the **primary Roster screen**, populated with the real sample data below.
If you have room, add the **Character Detail** view as a second state (toggle/route within the same page).
Make it look *stunning* — this is the hero artifact that sells the whole project.

## Platforms & responsiveness (required)

- **Desktop is primary** (≥1100px): a left sidebar shell + a wide content area.
- Must be **fully responsive** down to a phone (it will later ship as an installable PWA / Android app).
  On narrow screens the sidebar collapses to a **bottom tab bar**, the summary stats wrap, and cards go
  single-column. No horizontal scrolling of the page body ever.

## The theme — *Midnight*

*Midnight* is WoW's void-invasion expansion set in the elven homeland of **Quel'Thalas** and its
golden **Sunwell**. Its identity is **eclipse**: the sun blotted out, the world thrown into a beautiful,
dangerous twilight — **void magenta bleeding across a starlit indigo sky**, with **Sunwell gold** as the
last thread of Light fighting through. Antagonist energy: Xal'atath the Harbinger, void tendrils, the Old
God whisper. Elven-noble architecture: engraved geometry, crescent moons, high-elf filigree.

Lean into this hard. This is the one place to be bold. Some anchors (adjust freely, keep the spirit):

- **Palette (dark-first — commit to the night):**
  - Ground / void: `#07060E`, deep-space indigo `#0B0A18`
  - Panels: midnight `#141028`, raised `#1B1636`
  - **Primary accent — void corona:** magenta-violet `#B15CFF` (glow `#C77DFF`, deep `#7A2FD6`)
  - **Secondary accent — Sunwell gold** (the eclipsed Light; use sparingly for prestige/emphasis):
    `#F3C766` / `#E7A93A`
  - Starlight text / highlights: `#EDE9FF`, muted `#A79FC8`
  - Void abyss depth for shadows/gradients: `#241A52`
  - Semantic: good `#6FE0C0` (starlit teal), warning gold `#E7A93A`, danger `#E0435B` (Quel'Thalas red)
- **Motif ideas** (pick what serves the design, don't cram all in): an **eclipse** as the signature
  graphic (dark disc + shimmering void corona) in the header or empty state; a faint **drifting
  starfield** behind the shell; hairline **elven-filigree** dividers or corner flourishes; **crescent
  moon** iconography; void-tendril texture at very low opacity. Keep it elegant, never noisy — the data
  must stay the star.
- **Typography:** an engraved, noble **display** face for headings and character names (e.g. *Cinzel*,
  *Marcellus SC*, or *Cormorant* — via Google Fonts, inlined/linked from fonts.googleapis.com only),
  paired with a clean, modern **body** face (*Inter* / *Barlow*), and **tabular-figure numerals** for all
  stats (a condensed or mono face like *Barlow Condensed* / *JetBrains Mono*). Uppercase, letter-spaced
  eyebrow labels (`ITEM LEVEL`, `MYTHIC+`, `RAID`) are on-brand for both WoW and this app.
- **Motion** (respect `prefers-reduced-motion`): a subtle ambient starfield; a soft eclipse-corona pulse;
  card hover that lifts and **ignites a class-coloured edge**; stat numbers that count up on load;
  slumbering cards that breathe a slow, sleepy shimmer.

## Class colours (authentic — players expect these exactly)

Use each character's class colour for their **name** and as the card's identity accent. Canonical hexes:

| Class | Hex | Class | Hex |
|---|---|---|---|
| Warrior | `#C69B6D` | Monk | `#00FF98` |
| Paladin | `#F48CBA` | Druid | `#FF7C0A` |
| Hunter | `#AAD372` | Demon Hunter | `#A330C9` |
| Rogue | `#FFF468` | Evoker | `#33937F` |
| Priest | `#FFFFFF` | Death Knight | `#C41E3A` |
| Shaman | `#0070DD` | Mage | `#3FC7EB` |
| Warlock | `#8788EE` | | |

Faction accents: **Alliance** cool blue `#4A7FD6`, **Horde** blood red `#C4232B` — use as a small tag,
never as the card's main colour (class colour wins).

## Layout — the Roster screen

1. **Sidebar (desktop) / bottom tab bar (mobile):**
   - App crest + wordmark "WoW ROSTER" with a small eclipse/crescent mark.
   - Nav: **Roster** (active), **Character** (detail, contextual), **Collections**, **Settings**.
   - Footer block: the tracked account/region (e.g. "EU · Draenor"), a **theme toggle** (Midnight ↔ an
     optional lighter "Dawn/Sunwell" variant), and a small "Refresh" affordance.
2. **Header:** page title **ROSTER** in the engraved display face, an eyebrow above it
   (`YOUR CHARACTERS · MIDNIGHT`), and on the right an **"+ Add Character"** button + a region/realm/name
   quick-add.
3. **Summary bar** — a row of big-number stat cards summarising the whole roster (see Progress-style
   insight cards): **Characters**, **Avg Item Level**, **Top M+ Rating**, **Raid-Ready** (count at/above a
   threshold), **Total Achievements**. Big numerals, uppercase labels.
4. **Character grid** — responsive cards (≥340px each on desktop, 1-col on mobile). This is the heart of
   the page; spend your craft here.
5. **Empty state** — the eclipse graphic + "No characters yet — add one above. Only recently-active
   characters return data."
6. **Footer line:** "Data: Blizzard Battle.net API · retail (Midnight)".

## The Character Card — spec it precisely

Each card renders one character. Fields we actually have (design around exactly these):

- **Portrait** — a full-body character render. IMPORTANT: real render images come from an external host
  that won't load in a self-contained mockup, so **design the portrait as a class-crest / void-silhouette
  treatment** (CSS/SVG, tinted with the class colour) that looks finished on its own **and** leaves a slot
  a real image can drop into later. Make the fallback genuinely beautiful, not a grey box.
- **Name** — in the class colour, engraved display face, prominent.
- **Title** — italic Sunwell-gold, small (e.g. "the Draconic Hero"). Optional per character.
- **Identity line** — `Realm · REGION · Lvl 90 Night Elf Destruction Warlock`.
- **Stat chips** — pill row: **ilvl** (gold-tinted number), **M+** rating (teal number), **raid** progress
  like `8/8H` (green), then one chip per **profession**.
- **Guild · Faction** — `‹CMT› · Alliance`, small, with the faction accent.
- **Last seen** — relative time (e.g. "2 days ago"), quiet.
- **Remove control** — an unobtrusive ✕ on hover.

### Card states (all must be designed)

- **Rich / max-level** — everything populated (the showcase state). Give this the full treatment: class-
  colour edge glow on hover, ilvl in Sunwell gold, a subtle prestige feel for high M+ / full raid clears.
- **Levelling** — a lower-level character (e.g. Lvl 79), no M+/raid yet; show a level or XP hint instead.
- **Slumbering** — the player's account is inactive, so the API returns nothing for this character. Show a
  **greyed, dormant card**: desaturated, a crescent-moon "asleep" mark, a line like "⚠ slumbering —
  resub & log in once to wake." It should read as *sleeping under the eclipse*, poetic not broken.

## Character Detail view (second state, if you have room)

A hero band (large portrait/crest, class-coloured name, title, guild, ilvl + M+ + raid headline) over a
starfield, then sections:

- **Gear** — every equipped slot: item name, item level, quality colour (Common→Legendary), gem/enchant
  markers. A tidy two-column slot list or paperdoll-style ring.
- **Mythic+** — season rating with a **tier track** (hexagon milestone nodes on a progress line, à la a
  rank ladder) + the best recent runs (`+18 Ara-Kara`, dungeon names + key levels).
- **Raid** — the current raid, progress per difficulty (Normal / Heroic / Mythic) as segmented bars.
- **Collections** — mounts and pets counts as big numbers.
- **Professions** — each profession with its tier/skill.

## Sample data — populate the mockup with this exact roster

(Character 1 is real; the rest are realistic samples so every class colour and state shows. Use them
verbatim so the page is full of true-feeling content, never lorem.)

| # | Name | Race / Class / Spec | Faction | Lvl | ilvl | M+ | Raid | Professions | Guild | Title | Last seen | State |
|---|------|--------------------|---------|-----|------|----|----|-------------|-------|-------|-----------|-------|
| 1 | **Loonwhy** | Night Elf **Warlock** (Destruction) | Alliance | 90 | 312 | 3409 | 8/8H | Enchanting | ‹CMT› | the Draconic Hero | 2d ago | rich |
| 2 | **Voidfang** | Void Elf **Demon Hunter** (Havoc) | Alliance | 90 | 318 | 3610 | 8/8H | — | ‹CMT› | Sha'tari Defender | 5h ago | rich |
| 3 | **Sunwarden** | Blood Elf **Paladin** (Retribution) | Horde | 90 | 305 | 2740 | 6/8H | Jewelcrafting, Blacksmithing | ‹Eclipse› | the Lightbringer | 1d ago | rich |
| 4 | **Emberwing** | Dracthyr **Evoker** (Devastation) | Alliance | 90 | 300 | 2510 | 5/8H | Alchemy, Herbalism | ‹CMT› | — | 3d ago | rich |
| 5 | **Thornhide** | Tauren **Druid** (Guardian) | Horde | 90 | 296 | 2210 | 8/8N | Leatherworking, Skinning | ‹Eclipse› | — | 4d ago | rich |
| 6 | **Frostveil** | Troll **Mage** (Frost) | Horde | 88 | 284 | 1980 | 3/8N | Tailoring | ‹Eclipse› | — | 6d ago | rich |
| 7 | **Ironhowl** | Orc **Warrior** (Arms) | Horde | 79 | 210 | — | — | Mining | — | — | 1w ago | levelling |
| 8 | **Nightwhisper** | Night Elf **Priest** (Shadow) | Alliance | 90 | — | — | — | — | ‹CMT› | — | 47d ago | slumbering |

**Roster summary (derive from the above):** 8 characters · avg ilvl ≈ 292 (of the awake ones) · top M+
3610 · raid-ready 4 · total achievements ~180k.

## Technical constraints (self-contained page)

- **One HTML file**, all CSS and JS inline. No external assets **except Google Fonts** (link from
  `fonts.googleapis.com`). No external images — build portraits/crests and all graphics with CSS/SVG.
- **Theme-aware & accessible:** dark-first Midnight palette on `:root`; if you add the light "Dawn"
  variant, drive it entirely through CSS tokens so both themes stay legible; visible keyboard focus;
  `prefers-reduced-motion` honoured; body has an explicit token background (never transparent).
- **Class colours as CSS custom properties** (the table above), applied per card.
- **Tabular numerals** everywhere numbers align; wide content scrolls inside its own container, never the
  page body.
- Title the page **"WoW Roster"**.

## The one-line pitch to hold in your head

*A command console for your whole roster, seen through the eclipse of Midnight — void-violet and starlight
over the sleeping Sunwell, every character a jewel of its class colour.*
