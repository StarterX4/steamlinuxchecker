# SteamLinuxChecker
Ever wondered if you're a true Linux gamer?

# Dependencies
Requires `python3.5+`.

# Installation
Example installation instructions on Debian-like systems:

```sh
$ sudo apt-get install python3.5
$ git clone --recursive --depth 1 https://gitlab.com/lue-gamers/steamlinuxchecker.git
$ cd steamlinuxchecker
$ cp config_example.ini config.ini
$ vi config.ini # set your Steamp API key https://steamcommunity.com/dev/apikey
$ ./checkuser {profile_url|vanity_name|profile_id}
$ ./checkgroup {group_name}
```

# Usage

```sh
./checkuser $SteamID
```

SteamID can be any of the following format:
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
