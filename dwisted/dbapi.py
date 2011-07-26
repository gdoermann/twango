from django.db import connections as django_connections
from twisted.enterprise import adbapi
from django.core.exceptions import ImproperlyConfigured

ENGINE_MAP = {
    'postgresql_psycopg2':'pyPgSQL.PgSQL',
    'mysql':'MySQLdb',
}

class TwistedConnections:
    def __init__(self):
        self.databases = django_connections.databases
        self._connections = {}

    def __getitem__(self, alias):
        if alias in self._connections:
            return self._connections[alias]
        django_connections.ensure_defaults(alias)
        db = self.databases[alias]
        engine = db['ENGINE']
        name = engine.split('.')[-1]
        if not ENGINE_MAP.has_key(name):
            raise ImproperlyConfigured('Database backend not supported: %s' %engine)

        connection = adbapi.ConnectionPool(ENGINE_MAP[name], db['NAME'], db['USER'], db['PASSWORD'])
        self._connections[alias] = connection
        return connection

    def __iter__(self):
        return iter(self.databases)

    def all(self):
        return [self[alias] for alias in self]

connections = TwistedConnections()