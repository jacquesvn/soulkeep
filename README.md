# WoW Roster (working title) — retail character management app

## v1 scope
API-only roster dashboard (no in-game addon): all your alts, ilvl, gear, spec, professions,
M+ rating, raid progression, last-played — from Blizzard's free REST API. Weekly-chores
(vault/lockouts/currencies) is a later module via a companion addon, if wanted.

## Register a dev app (one-time, ~2 min — you must do this, it needs your Battle.net login)
1. Go to https://develop.battle.net/  and sign in with your Battle.net account.
2. "API Access" → "Create Client" (aka https://develop.battle.net/access/clients).
3. Name it anything (e.g. "WoW Roster"); Redirect URL can be `https://localhost` for now
   (only needed later for the user-login/roster feature). Intended use: personal project.
4. Copy the **Client ID** and **Client Secret**.

## Run the spike
    cp bnet.env.example bnet.env    # then paste your Client ID + Secret into bnet.env
    python spike.py <region> <realm-slug> <character-name>
    # e.g.  python spike.py us area-52 mycharacter
    #   region = us | eu | kr | tw ;  realm-slug = lowercase, hyphenated (e.g. "area-52")

Prints the character summary/gear/M+/professions and dumps raw JSON to last_profile.json.
