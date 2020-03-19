import sys
import configparser
import requests


config = configparser.ConfigParser()
config.read('config.ini')

if (not config.has_option('api', 'key')):
    raise SystemExit("Can't find api.key in `config.ini` file.");

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

def get_user_games(id):
    key = config['api'].get('key')
    data = get_json(f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={id}")
    return data['response']['games']

def check_steam_user(id, verbose = False):
    forever_total = 0
    linux = mac = windows = 0
    ignore_appids = config['scan'].get('ignore_appids').split() if config.has_option('scan', 'ignore_appids') else []
    try:
        games = get_user_games(id)
        count = len(games)
        for i, game in enumerate(games, start = 1):
            if  str(game['appid']) in ignore_appids:
                continue
            forever_total += game['playtime_forever']
            linux += game['playtime_linux_forever']
            mac += game['playtime_mac_forever']
            windows += game['playtime_windows_forever']
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
