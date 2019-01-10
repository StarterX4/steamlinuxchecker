# SteamLinuxChecker
Ever wondered if you're a true Linux gamer?

# Dependencies
Requires `python3.5`, depends on [Steam API key](https://steamcommunity.com/dev/apikey)
and community powered [SteamDB Linux games list](https://github.com/SteamDatabase/SteamLinux).

# Installation
Example installation instructions on Debian-like systems:

```sh
$ sudo apt-get install python3.5
$ git clone --recursive --depth 1 https://gitlab.com/lue-gamers/steamlinuxchecker.git
$ cd steamlinuxchecker
$ cp config_example.ini config.ini
$ vim config.ini # set your Steamp API key in here
$ ./checkuser {profile_url|vanity_name|profile_id}
$ ./checkgroup {group_name}
```

# Usage
* https://steamcommunity.com/id/cprn
* https://steamcommunity.com/profiles/76561198090757837
* https://steamcommunity.com/groups/LinuxUsersExclusively

Both `cprn` and `76561198090757837` will work for `checkuser`.
The name of the group `LinuxUsersExclusively` will work for `checkgroup`.

# Updating
To update you can either backup your local `config.ini` and redo the installation
process or call:

```sh
$ cd steamlinuxchecker
$ git pull
$ git submodule update --recursive --init # if dependencies changed
```

# Notes
Platform data is stored in simple file based cache in `~/tmp/steamwww_cache.pkl`.
First run might be slow, next runs should have most of the platform info cached.
Cached data older than 90 days is refreshed to handle adding or dropping Linux support.

# Troubleshooting
If you're having a lot of false positives (as in games that run on Linux but the
script is showing they don't) it's probably because your IP is based in Germany
(where for some reason Valve decided to display different platform icons than
for the rest of the World). You can try to use an HTTP proxy like so:

    https_proxy=http://<proxy_ip>:<proxy_port> ./checkuser cprn

If some particular proxy doesn't work for you, try one or two others before
giving up. A list of free HTTPS proxies: https://www.sslproxies.org/. Don't
forget to remove your cache first.