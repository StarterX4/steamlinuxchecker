Import/fork from https://gitlab.com/lue-gamers/steamlinuxchecker

# SteamLinuxChecker
Ever wondered if you're a true Linux gamer?

# Dependencies
Requires `python3.5+`.

# Installation
Installation instructions:

```sh
$ git clone --depth 1 https://gitlab.com/lue-gamers/steamlinuxchecker.git
$ cd steamlinuxchecker
$ cp -n config_example.ini config.ini
```

Edit `config.ini` and paste in [your Steam API key](https://steamcommunity.com/dev/apikey).

# Usage
```sh
./checkuser {steam_id}
```

Steam ID can be any of the following:
* https://steamcommunity.com/id/cprn
* https://steamcommunity.com/profiles/76561198090757837
* cprn
* 76561198090757837

# Updating
```sh
$ cd steamlinuxchecker
$ git pull
```
Check `config_example.ini` for new options.
