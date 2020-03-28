import sys
import configparser
import locale
import requests
from datetime import datetime
from model import db, User, Game, Group, Playtime, Membership


config = configparser.ConfigParser()
config.read('config.ini')
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

if not config.has_option('api', 'key'):
    raise SystemExit("Can't find api.key in `config.ini` file.")

def get_json(url):
    try:
        r = requests.get(url)
        assert r.status_code == 200, f"Can't open url ({r.status_code})"
        return r.json()
    except:
        print(r.json())
        raise SystemExit()

def get_steam_id(id):
    for unwanted in ['http://steamcommunity.com/id/', 'https://steamcommunity.com/id/', 'http://steamcommunity.com/profiles/', 'https://steamcommunity.com/profiles/', '/']:
        id = id.replace(unwanted, '')
    if len(id) == 17 and id.isdigit():
        return id
    key = config['api'].get('key')
    data = get_json(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={key}&vanityurl={id}")
    return data['response']['steamid']

def get_user(id):
    user = User(id).read()
    if user.persona is None:
        user_data = get_user_data(user.id)
        user = User(user.id,
                    user_data['personaname'],
                    user_data['realname'],
                    user_data['profileurl'],
                    user_data['avatarfull']
                    )
        user.save()
    return user

def get_user_data(id):
    return get_users_data([id])[0]

def get_users_data(ids):
    key = config['api'].get('key')
    data = get_json(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={','.join(ids)}")
    return data['response']['players']

def get_user_games(id):
    key = config['api'].get('key')
    data = get_json(f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={id}")
    return data['response']['games']

def get_game(id):
    game = Game(id).read()
    if game.name is None:
        game_data = get_game_data(game.id)
        release_date = datetime.strptime(f"{game_data['release_date']['date']}", '%d %b, %Y')
        game = Game(game.id,
                    game_data['name'],
                    game_data['header_image'],
                    game_data['platforms']['linux'],
                    game_data['platforms']['mac'],
                    game_data['platforms']['windows'],
                    release_date
                    )
        game.save()
        raise SystemExit('will not risk ban')
    return game

def get_game_data(appid):
    data = get_json(f"https://store.steampowered.com/api/appdetails/?appids={appid}&filters=basic,platforms,release_date")
    return data[str(appid)]['data']

def check_steam_user(id, verbose=False):
    user = get_user(id)
    forever_total = 0
    linux = mac = windows = 0
    ignore_appids = config['scan'].get('ignore_appids').split() if config.has_option('scan', 'ignore_appids') else []
    try:
        user_games = get_user_games(id)
        count = len(user_games)
        for i, user_game in enumerate(user_games, start = 1):
            if  str(user_game['appid']) in ignore_appids:
                continue
            game = get_game(user_game['appid'])
            forever_total += user_game['playtime_forever']
            linux += user_game['playtime_linux_forever']
            mac += user_game['playtime_mac_forever']
            windows += user_game['playtime_windows_forever']
            verbose and print_progress(i, count)
    except KeyError:
        verbose and print(f"SteamID {id} private")

    platform_total = linux + mac + windows
    verbose and print_user_summary(id, forever_total, platform_total, linux, mac, windows)
    return forever_total, platform_total, linux, mac, windows

def print_progress(iteration, total):
    percent = ("{0:.2f}").format(100 * (iteration / float(total)))
    sys.stderr.write(28 * ' ' + '\r')
    sys.stderr.flush()
    sys.stderr.write(' {:5} / {} ({}%)\r'.format(iteration, total, percent))
    sys.stderr.flush()

def print_user_summary(id, forever_total, platform_total, linux, mac, windows):
    score = 0
    if platform_total > 0:
        score = linux/platform_total
    sys.stdout.write("\nSteamID: {}\nTotal: {:5d}h {:2d}m\nLinux: {:5d}h {:2d}m\nScore: {:10.2%}\n".format(
        id,
        *divmod(platform_total, 60),
        *divmod(linux, 60),
        score
    ))
    sys.stdout.flush()
