import sys
import configparser
from steamapi import steamapi
from steamwww import Scraper


scraper = Scraper()
config = configparser.ConfigParser()
config.read('config.ini')


def get_steam_api():
    try:
        steamapi.core.APIConnection(api_key=config['api'].get('key'))
    except KeyError:
        raise SystemExit('Copy config_example.ini to config.ini and set the api.key value!')
    return steamapi

def get_steam_user(steamapi, id):
    try:
        try:
          user = steamapi.user.SteamUser(userid=int(id))
        except ValueError:
          user = steamapi.user.SteamUser(userurl=id)
    except steamapi.errors.UserNotFoundError:
        raise SystemExit('User not found.')
    return user

def check_steam_user(user, verbose = False):
    total = 0
    linux = 0
    try:
        count = len(user.games)
        for i, game in enumerate(user.games, start = 1):
            if config['scan'].getboolean('ignore_zero_playtime') and game.playtime_forever == 0:
                continue
            total += game.playtime_forever
            badge = '-----'
            if scraper.runs_on_linux(game.id, verbose):
                badge = 'LINUX'
                linux += game.playtime_forever
            verbose and print_with_progress(badge + ' %6s ' % game.playtime_forever + game.name, i, count)
    except steamapi.errors.AccessException:
        user.name += ' (private)'

    score = 0
    if total > 1:
        score = linux/total

    stats = (total, linux, score)
    verbose and print_user_summary(user, stats)
    return stats

def print_with_progress(message, iteration, total):
    l = len(str(total))
    percent = ("{0:.2f}").format(100 * (iteration / float(total)))
    sys.stderr.write(28 * ' ' + '\r')
    sys.stderr.flush()
    sys.stdout.write(message + '\n')
    sys.stdout.flush()
    sys.stderr.write(' {:5} / {} ({}%)\r'.format(iteration, total, percent))
    sys.stderr.flush()

def print_user_summary(user, stats):
    sys.stdout.write("\nSteamID: {}\nUser: {}\nProfile: {}\nTotal: {:5d}h {:2d}m\nLinux: {:5d}h {:2d}m\nScore: {:10.2%}\n".format(
        user.id,
        user.name,
        user.profile_url,
        *divmod(stats[0], 60),
        *divmod(stats[1], 60),
        stats[2]
    ))
    sys.stdout.flush()
