#!/usr/bin/env python3
"""Find a top, currently-active character via the M+ leaderboards and dump the FULL rich profile,
so we can see every field a roster dashboard could surface. Stdlib only."""
import sys, spike, urllib.parse

def rid(href):  # extract trailing numeric id from an API href
    return href.rstrip('/').split('/')[-1].split('?')[0]

def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    region = sys.argv[1] if len(sys.argv) > 1 else 'us'
    dyn, pns = f'dynamic-{region}', f'profile-{region}'
    cid, sec = spike.load_creds(); tok = spike.get_token(cid, sec)

    period = spike.api_get(region, '/data/wow/mythic-keystone/period/index', tok, dyn)['current_period']['id']
    BIG = {'eu': ['draenor', 'silvermoon', 'kazzak', 'twisting-nether', 'ravencrest', 'tarren-mill'],
           'us': ['illidan', 'area-52', 'stormrage', 'tichondrius', 'sargeras', 'frostmourne']}
    realms = BIG.get(region, ['draenor'])
    print(f'[find] region={region} period={period}, scanning big-realm current leaderboards...')

    def resolve_cr(slug):
        r = spike.api_get(region, f'/data/wow/realm/{slug}', tok, dyn)
        return rid(r['connected_realm']['href']) if not r.get('_error') else None

    top = None
    for ptry in [period, period - 1, period - 2]:          # current period, then recent fallbacks
        for slug in realms:
            crid = resolve_cr(slug)
            if not crid:
                continue
            idx = spike.api_get(region, f'/data/wow/connected-realm/{crid}/mythic-leaderboard/index', tok, dyn)
            for lbd in (idx.get('current_leaderboards') or []):   # the realm's CURRENT dungeons only
                lb = spike.api_get(region, f'/data/wow/connected-realm/{crid}/mythic-leaderboard/{lbd["id"]}/period/{ptry}', tok, dyn)
                groups = lb.get('leading_groups') or []
                if groups and groups[0].get('members'):
                    m = groups[0]['members'][0]['profile']
                    top = (m['realm']['slug'], m['name'], lbd.get('name'), groups[0].get('keystone_level'), ptry)
                    break
            if top: break
        if top: break
    if not top:
        sys.exit('No populated leaderboard found across scanned realms/periods — M+ season may be off.')

    realm, name, dun, klvl, used_period = top
    print(f'[find] -> {name} @ {realm} (led a +{klvl} {dun}, period {used_period})\n')
    base = f'/profile/wow/character/{urllib.parse.quote(realm)}/{urllib.parse.quote(name.lower())}'
    g = lambda p: spike.api_get(region, base + p, tok, pns)
    prof, eq, mpl = g(''), g('/equipment'), g('/mythic-keystone-profile')
    raids, mounts, pets = g('/encounters/raids'), g('/collections/mounts'), g('/collections/pets')
    profs, media = g('/professions'), g('/character-media')

    print('================ FULL CHARACTER ================')
    print(f"  {prof.get('name')} - {prof.get('realm',{}).get('name')} ({region.upper()})")
    print(f"  Level {prof.get('level')}  {prof.get('race',{}).get('name')} "
          f"{prof.get('active_spec',{}).get('name')} {prof.get('character_class',{}).get('name')}  "
          f"[{prof.get('faction',{}).get('name')}]")
    print(f"  Guild: {prof.get('guild',{}).get('name') or '-'}   Title: {prof.get('active_title',{}).get('name') or '-'}")
    print(f"  Item level: equipped {prof.get('equipped_item_level')} / avg {prof.get('average_item_level')}")
    print(f"  Achievements: {prof.get('achievement_points')} pts")

    print('\n-- MYTHIC+ --')
    print(f"  Season rating: {round(mpl.get('current_mythic_rating',{}).get('rating',0),1) if not mpl.get('_error') else 'n/a'}")
    for r in (mpl.get('current_period',{}).get('best_runs') or [])[:5] if not mpl.get('_error') else []:
        print(f"    +{r.get('keystone_level')}  {r.get('dungeon',{}).get('name')}")

    print('\n-- RAID PROGRESS (latest expansion) --')
    exps = raids.get('expansions') or []
    if exps and not raids.get('_error'):
        latest = exps[-1]
        print(f"  {latest.get('expansion',{}).get('name')}:")
        for inst in latest.get('instances', [])[-3:]:
            for mode in inst.get('modes', []):
                p = mode.get('progress', {})
                print(f"    {inst.get('instance',{}).get('name')} [{mode.get('difficulty',{}).get('name')}]: "
                      f"{p.get('completed_count')}/{p.get('total_count')} bosses")

    print('\n-- COLLECTIONS --')
    print(f"  Mounts: {len(mounts.get('mounts') or []) if not mounts.get('_error') else '?'}   "
          f"Pets: {len(pets.get('pets') or []) if not pets.get('_error') else '?'}")

    print('\n-- PROFESSIONS --')
    for p in (profs.get('primaries') or []):
        print(f"  {p.get('profession',{}).get('name')}: "
              f"{', '.join(t.get('tier',{}).get('name','') for t in (p.get('tiers') or []))}")

    print('\n-- EQUIPMENT (top 6 by ilvl) --')
    items = sorted((eq.get('equipped_items') or []), key=lambda i: -(i.get('level',{}).get('value') or 0))
    for it in items[:6]:
        print(f"    {it.get('slot',{}).get('name'):12} ilvl {it.get('level',{}).get('value'):>4} [{it.get('quality',{}).get('name')}] {it.get('name')}")

    print(f"\n-- MEDIA --  render available: {'yes' if not media.get('_error') else 'no'}")
    import json
    json.dump({'profile':prof,'equipment':eq,'mplus':mpl,'raids':raids,'mounts_ct':len(mounts.get('mounts') or []),
               'pets_ct':len(pets.get('pets') or []),'professions':profs,'media':media},
              open('showcase_profile.json','w',encoding='utf-8'), indent=2)
    print('[OK] full JSON -> showcase_profile.json')

if __name__ == '__main__':
    main()
