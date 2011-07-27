from django.db import connections as django_connections
from twisted.enterprise import adbapi
from django.core.exceptions import ImproperlyConfigured

class TwistedConnections:
    def __init__(self):
        self.databases = django_connections.databases
        self._connections = {}

    def __getitem__(self, alias):
        if alias in self._connections:
            return self._connections[alias]
        django_connections.ensure_defaults(alias)
        db = self.databases[alias]
        connection = adbapi.ConnectionPool(db['ENGINE'], db['NAME'], db['USER'], db['PASSWORD'])
        self._connections[alias] = connection
        return connection

    def __iter__(self):
        return iter(self.databases)

    def all(self):
        return [self[alias] for alias in self]

connections = TwistedConnections()