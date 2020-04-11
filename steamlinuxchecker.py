import configparser
import locale
import sys
import re
from datetime import datetime
from time import sleep

import requests
from model import User, Game, Scan, Playtime


config = configparser.ConfigParser(inline_comment_prefixes=('#',))
config.read('config.ini')
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

if not config.has_option('api', 'key'):
    raise SystemExit("Can't find api.key in `config.ini` file.")

def get_json(url):
    wait_seconds = config['scan'].get('seconds_between_steam_api_calls') or 3
    wait_seconds = float(wait_seconds)
    if hasattr(get_json, 'last_call'):
        seconds_since = (datetime.utcnow() - get_json.last_call).total_seconds()
        if seconds_since < wait_seconds:
            sleep(wait_seconds - seconds_since)
    get_json.last_call = datetime.utcnow()
    try:
        r = requests.get(url)
        assert r.status_code == 200, f"Can't open url: {url} ({r.status_code})"
        return r.json()
    except:
        print(f"HTTP 200 OK: {url}\nError: malformed JSON:\n{r.json()}")
        raise SystemExit()

def get_page(url):
    r = requests.get(url)
    assert r.status_code == 200, "Can't open %s (%d)" % (url, r.status_code)
    return r.text

def get_steam_id(id):
    for unwanted in ['http://', 'https://', 'steamcommunity.com/profiles/', 'steamcommunity.com/id/', '/']:
        id = id.replace(unwanted, '')
    if len(id) == 17 and id.isdigit():
        return int(id)
    key = config['api'].get('key')
    data = get_json(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={key}&vanityurl={id}")
    return data['response']['steamid']

def get_user(id):
    user = User(id).read()
    if user.visibility_state is None:
        user_data = get_user_data(user.id)
        user = User(user.id,
                    user_data['personaname'] if 'personaname' in user_data.keys() else None,
                    user_data['realname'] if 'realname' in user_data.keys() else None,
                    user_data['profileurl'],
                    user_data['avatarfull'],
                    user_data['communityvisibilitystate']
                    )
        user.save()
    return user

def get_user_data(id):
    return get_users_data([id])[0]

def get_users_data(ids):
    key = config['api'].get('key')
    ids = [str(id) for id in ids]
    data = get_json(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={','.join(ids)}")
    return data['response']['players']

def get_user_games(id):
    key = config['api'].get('key')
    data = get_json(f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={id}")
    return data['response'].get('games') or []

def get_group_id(id):
    if len(id) == 18 and id.isdigit():
        return int(id)
    for unwanted in ['http://', 'https://', 'steamcommunity.com/groups/', '/']:
        id = id.replace(unwanted, '')
    return id

def get_group_members(id):
    xml = get_page(f'http://steamcommunity.com/groups/{id}/memberslistxml/?xml=1')
    rx = re.compile(r'steamID64>(\d+)')
    ids = []
    for match in rx.finditer(xml):
        ids.append(match.group(1))
    return sorted(ids)

def get_game(id):
    return Game(id)

def add_playtime(scan, game, user_game):
    strategy = config['scan'].get('save_playtime') or 0
    strategy = int(strategy)
    if strategy == 0:
        return
    playtime = Playtime(scan.id,
             game.id,
             user_game['playtime_linux_forever'],
             user_game['playtime_mac_forever'],
             user_game['playtime_windows_forever'],
             user_game['playtime_forever'])
    if strategy == 1:
        should_save = playtime.linux + playtime.mac + playtime.windows > 0
    if strategy == 8:
        should_save = playtime.total > 0
    should_save and playtime.save()

def get_game_data(appid):
    data = get_json(f"https://store.steampowered.com/api/appdetails/?appids={appid}&filters=basic,platforms")
    try:
        return data[str(appid)]['data']
    except KeyError:
        return None

def check_steam_user(id, verbose=False):
    user = get_user(id)
    scan = Scan(user.id)
    if not user.public():
        return scan
    scan.save()
    forever_total = 0
    linux = mac = windows = 0
    ignore_appids = config['scan'].get('ignore_appids') or ''
    try:
        user_games = get_user_games(user.id)
        count = len(user_games)
    except KeyError as e:
        verbose and print(f"SteamID {user.id} playtime inaccessible: {e}")
        return scan
    try:
        for i, user_game in enumerate(user_games, start=1):
            if  str(user_game['appid']) in ignore_appids:
                continue
            game = get_game(user_game['appid'])
            add_playtime(scan, game, user_game)
            forever_total += user_game['playtime_forever']
            linux += user_game['playtime_linux_forever']
            mac += user_game['playtime_mac_forever']
            windows += user_game['playtime_windows_forever']
            verbose and print_progress(i, count)
    except KeyError as e:
        verbose and print(f"AppID {user_game['appid']} details inaccessible: {e}")
        return scan
    scan.total = forever_total
    scan.linux = linux
    scan.mac = mac
    scan.windows = windows
    scan.save()
    return scan

def print_progress(iteration, total):
    percent = ("{0:.2f}").format(100 * (iteration / float(total)))
    sys.stderr.write(28 * ' ' + '\r')
    sys.stderr.flush()
    sys.stderr.write(' {:5} / {} ({}%)\r'.format(iteration, total, percent))
    sys.stderr.flush()

def print_scan_summary(scan):
    user = get_user(scan.user_id)
    if user.public():
        platform_total = scan.linux + scan.mac + scan.windows
        total_h, total_m = divmod(scan.total, 60)
        linux_h, linux_m = divmod(scan.linux, 60)
        mac_h, mac_m = divmod(scan.mac, 60)
        windows_h, windows_m = divmod(scan.windows, 60)
    else:
        total_h = total_m = linux_h = linux_m = mac_h = mac_m = windows_h = windows_m = platform_total = 0
        sys.stdout.write(f"\nPRIVATE ACCOUNT")
    score = 0
    if platform_total > 0:
        score = scan.linux/platform_total
    pad = 16
    pad_h = pad - 5
    sys.stdout.write(f"\n{user.profile_url}\n"
                     f"SteamID: {user.id: >{pad + 2}}\n"
                     f"Persona:   {str(user.persona): >{pad}}\n"
                     f"Name:      {str(user.name): >{pad}}\n"
                     f"Linux:     {linux_h: >{pad_h}}h {linux_m: >2}m\n"
                     f"Mac:       {mac_h: >{pad_h}}h {mac_m: >2}m\n"
                     f"Windows:   {windows_h: >{pad_h}}h {windows_m: >2}m\n"
                     f"Total:     {total_h: >{pad_h}}h {total_m: >2}m\n"
                     f"Score:     {score: >{pad}.2%}\n")
    sys.stdout.flush()
