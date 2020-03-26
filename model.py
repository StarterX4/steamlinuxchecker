from datetime import datetime
from copy import copy
from sqlite3 import connect, OperationalError, Row


class Database:

    def __init__(self, path='database.sqlite3'):
        self.path = path
        self.connection = self._connect(path)
        self.connection.row_factory = Row
        self._update_schema()

    def _connect(self, path):
        try:
            return connect(path)
        except OperationalError as e:
            print(f"Can't connect to database, check write permissions for: {path}\nError: {e}")

    def _execute(self, query):
        try:
            return self.connection.cursor().execute(query)
        except OperationalError as e:
            print(f"Can't run query: {query}\nError: {e}")

    def _update_schema(self):
        self._execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY,
                      vanity TEXT,
                      image_url TEXT,
                      created TIMESTAMP,
                      updated TIMESTAMP)''')
        self._execute('''CREATE TABLE IF NOT EXISTS games (
                      id INTEGER PRIMARY KEY,
                      title TEXT,
                      image_url TEXT,
                      linux_support BOOLEAN,
                      mac_support BOOLEAN,
                      windows_support BOOLEAN,
                      created TIMESTAMP,
                      updated TIMESTAMP)''')
        self._execute('''CREATE TABLE IF NOT EXISTS groups (
                      id INTEGER PRIMARY KEY,
                      name TEXT,
                      image_url TEXT,
                      created TIMESTAMP,
                      updated TIMESTAMP)''')
        self._execute('''CREATE TABLE IF NOT EXISTS playtimes (
                      id INTEGER PRIMARY KEY,
                      user_id INTEGER,
                      game_id INTEGER,
                      linux_playtime INTEGER,
                      mac_playtime INTEGER,
                      windows_playtime INTEGER,
                      platform_playtime INTEGER,
                      total_playtime INTEGER,
                      date TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(id),
                      FOREIGN KEY (game_id) REFERENCES games(id))''')
        self._execute('''CREATE TABLE IF NOT EXISTS memberships (
                      id INTEGER PRIMARY KEY,
                      user_id INTEGER,
                      group_id INTEGER,
                      date TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(id),
                      FOREIGN KEY (group_id) REFERENCES groups(id))''')

    def _commit(self):
        self.connection.commit()

    def _table(self, entity):
        return f'{type(entity).__name__.lower()}s'

    def _table_info(self, table):
        result = self._execute(f'PRAGMA table_info({table})')
        return [dict(row) for row in result.fetchall()]

    def _primary_key(self, table):
        for row in self._table_info(table):
            if row['pk'] == 1:
                return row['name']
        raise KeyError(f'Primary key for table {table} not found')

    def _timestamped(self, table):
        for row in self._table_info(table):
            if row['name'] == 'created':
                return True
        return False

    def _fetch(self, table, where):
        result = self._execute(f'SELECT * FROM {table} WHERE {where}')
        return [dict(row) for row in result.fetchall()]

    def _changed(self, new, old):
        for param in vars(new):
            if getattr(old, param) != getattr(new, param):
                return True
        return False

    def _insert(self, table, data):
        columns = []
        values = []
        if self._timestamped(table):
            columns.append('created')
            columns.append('updated')
            values.append(f'"{datetime.utcnow()}"')
            values.append(f'"{datetime.utcnow()}"')
        for key, value in data.items():
            columns.append(key)
            values.append(f'"{value}"')
        self._execute(f'INSERT INTO {table} ({",".join(columns)}) VALUES ({",".join(values)})')
        self._commit()

    def _update(self, table, data, where):
        values = []
        if self._timestamped(table):
            values.append(f'updated = "{datetime.utcnow()}"')
        for key, value in data.items():
            values.append(f'{key} = "{value}"')
        self._execute(f'UPDATE {table} SET {",".join(values)} WHERE {where}')
        self._commit()

    def _where(self, entity, primary_key):
        return f'{primary_key} = {getattr(entity, primary_key)}'

    def read(self, entity):
        table = self._table(entity)
        primary_key = self._primary_key(table)
        where = self._where(entity, primary_key)
        db_values = self._fetch(table, where)
        if len(db_values) == 1:
            entity_from_db = copy(entity)
            entity_from_db.__dict__ = db_values[0]
            return entity_from_db

    def save(self, entity):
        table = self._table(entity)
        if self._timestamped(table):
            from_db = self.read(entity)
            if from_db is not None:
                if self._changed(entity, from_db):
                    where = self._where(entity, self._primary_key(table))
                    self._update(table, vars(entity), where)
                return
        self._insert(table, vars(entity))


class Entity:
    def save(self):
        db.save(self)

    def read(self):
        db.read(self)


class User(Entity):
    def __init__(self, id, vanity, image_url):
        self.id = id
        self.vanity = vanity
        self.image_url = image_url


class Game(Entity):
    def __init__(self, id, title, image_url, linux_support, mac_support, windows_support):
        self.id = id
        self.title = title
        self.image_url = image_url
        self.linux_support = linux_support
        self.mac_support = mac_support
        self.windows_support = windows_support


class Group(Entity):
    def __init__(self, id, name, image_url):
        self.id = id
        self.name = name
        self.image_url = image_url


class Playtime(Entity):
    def __init__(self, id, user_id, game_id, linux_playtime, mac_playtime, windows_playtime, platform_playtime, total_playtime, date):
        self.id = id
        self.user_id = user_id
        self.game_id = game_id
        self.linux_playtime = linux_playtime
        self.mac_playtime = mac_playtime
        self.windows_playtime = windows_playtime
        self.platform_playtime = platform_playtime
        self.total_playtime = total_playtime
        self.date = date


class Membership(Entity):
    def __init__(self, id, user_id, group_id, date):
        self.id = id
        self.user_id = user_id
        self.group_id = group_id
        self.date = date


db = Database()
