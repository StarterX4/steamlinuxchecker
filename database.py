from sqlite3 import connect, OperationalError


class Database:

    def __init__(self, path='database.sqlite3'):
        self.path = path
        self.connection = self._connect(path)
        self.update_schema()

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

    def _commit(self):
        self.connection.commit()

    def update_schema(self):
        self._execute('''create table if not exists users
                         (id integer, vanity text, image_url text, created text, updated text)''')
        self._execute('''create table if not exists games
                         (id integer, title text, image_url text, linux_support, mac_support, windows_support, created text, updated text)''')
        self._execute('''create table if not exists groups
                         (id integer, name text, image_url text, created text, updated text)''')
        self._execute('''create table if not exists user_games
                         (id, user_id integer, game_id integer, linux_playtime integer, mac_playtime integer, windows_playtime integer, platform_playtime integer, total_playtime integer, date text)''')
        self._execute('''create table if not exists user_groups
                         (id, user_id integer, group_id integer, date text)''')

    def insert(self, table, *data):
        values = []
        for v in data:
            values.append(f"\"{v}\"")
        self._execute(f"insert into {table} values ({','.join(values)})")
        self._commit()

    def update(self, table, where, **data):
        values = []
        for k, v in data.items():
            values.append(f"k = \"{v}\"")
        self._execute(f"update {table} set {','.join(values)} where {where}")
        self._commit()

    def remove(self, table, where):
        self._execute(f"delete from {table} where {where}")
        self._commit()

    def fetch(self, table, where):
        return self._execute(f"select * from {table} where {where}").fetchall()

    def tables(self):
        return self._execute("select name from sqlite_master").fetchall()
