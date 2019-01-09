#!/usr/bin/python3
import requests
import sys
import time
import json
from simplecache.cache import PickleCache


class Scraper:

    def __init__(self):
        self.__cache = PickleCache("~/tmp/steamwww_cache.pkl", 86400 * 90)
        self.__calls = 0
        with open('steamdb/GAMES.json') as steamdb:
            self.__steamdb = json.load(steamdb)

    def get_html(self, id): # TODO: retire
        self.__calls += 1
        self.__calls % 20 == 0 and time.sleep(2) # sometimes wait between calls
        r = requests.get('http://store.steampowered.com/app/%s' % id, cookies={
            'birthtime': '1000',
            'path': '/',
            'domain': 'store.steampowered.com'
            })
        assert r.status_code == 200, "Can't open %s (%d)" % (id, r.status_code)
        assert r.text.find('enter your birth') < 0, "Age check error! %d" % id
        return r.text

    def get_json(self, id):
        self.__calls += 1
        self.__calls % 20 == 0 and time.sleep(10) # extra sleep every 20 calls
        time.sleep(2) # sleep between each call
        url = 'https://store.steampowered.com/api/appdetails/?appids=%s&filters=basic,platforms,release_date'
        r = requests.get(url % id)
        try:
            j = r.json()[str(id)]
        except:
            print(r.json())
            raise SystemExit()
        assert r.status_code == 200, "Can't open %s (%d): %s" % (id, r.status_code, r.json())
        return j

    def runs_on_linux(self, id, verbose = False, cache = True, steamdb = True):
        try:
            if not cache:
                raise KeyError
            linux = self.__cache.get(id)['linux']
            verbose and print('   ', end = '')
        except KeyError:
            try:
                if not steamdb:
                    raise KeyError
                linux = self.__steamdb[str(id)]
                linux = True # TODO: filter hiddens, betas, etc.
            except KeyError:
                try:
                    j = self.get_json(id)
                    linux = j['data']['platforms']['linux'] if j['data']['type'] == 'game' else True
                except KeyError:
                    linux = False
            cache and self.__cache.add(id, {"linux": linux})
            cache and self.__cache.save()
            verbose and print(' + ', end = '')
        return linux


if __name__ == "__main__":
    print(Scraper().runs_on_linux(sys.argv[1]))
