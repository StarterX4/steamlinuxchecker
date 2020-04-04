# SteamLinuxChecker
Ever wondered if you're a true Linux gamer?

# Dependencies
Requires `python3.5+`.

# Installation
Example installation instructions on Debian-like systems:

```sh
$ sudo apt-get install python3
$ git clone --depth 1 https://gitlab.com/lue-gamers/steamlinuxchecker.git
$ cd steamlinuxchecker
$ cp config_example.ini config.ini
$ xdg-open config.ini # paste your Steam API key https://steamcommunity.com/dev/apikey
$ ./checkuser {profile_url}
```

# Usage

```sh
./checkuser $SteamID
```

SteamID can be any of the following formats:
* https://steamcommunity.com/id/cprn
* https://steamcommunity.com/profiles/76561198090757837
* cprn
* 76561198090757837

You can exclude `appids` in `config.ini`, for example to exclude
[Counter Strike](https://steamdb.info/app/730/) and
[Deathmatch Classic](https://steamdb.info/app/40/):

```ini
[scan]
ignore_appids = 730 40
```

# Updating

```sh
$ cd steamlinuxchecker
$ git pull
```

# TODO
Scanning whole groups.
