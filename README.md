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

## Run the desktop app
    cp bnet.env.example bnet.env    # then paste your Client ID + Secret into bnet.env
    pip install flask pywebview      # one-time
    python app.py                    # opens the WoW Roster desktop window

## Build the exe (portable)
    pip install pyinstaller pillow qrcode   # one-time
    python -m PyInstaller --noconfirm --onefile --noconsole --name WoWRoster --icon icon.ico --add-data "templates;templates" --add-data "addon;addon" --add-data "icon-192.png;." --add-data "icon-512.png;." --add-data "icon.ico;." --hidden-import qrcode app.py

`dist/WoWRoster.exe` is portable: it reads `bnet.env` and `roster.json` from the folder it sits in,
so copy those two files next to the exe. (dist/ is gitignored — the exe carries your API creds' folder.)

Add characters with the region/realm/name form in the header; remove with the ✕ on a card.
The roster is stored locally in `roster.json`. Only recently-active characters return data
(an unsubbed account's characters "slumber" and show a greyed card until you resub + log in once).

## Dev scripts
    python spike.py <region> <realm-slug> <character>    # raw pull -> last_profile.json
    python showcase.py [region]                          # find a top char -> showcase_profile.json
    python wowapi.py <region> <realm> <character>         # print the normalized character dict
    #   region = us | eu | kr | tw ;  realm-slug = lowercase, hyphenated (e.g. "area-52")
