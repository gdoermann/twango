from django.db.models.query import QuerySet
from django.db.models.sql.query import Query
from dwisted.dbapi import connections

class TwistedQuerySet(QuerySet):
    """ Methods:
            twisted
                Introspect database connection
                Create Twisted DB connection
                String Query from self.query
                Return deferred
            delete_twisted
            update_twisted
            count_twisted
            get_twisted
            create_twisted
            latest_twisted
    """
    def twisted(self):
        query = self.query
        assert(isinstance(query, Query))
        compiler = query.get_compiler(self.db)
        sql, params = compiler.as_nested_sql()
        if not sql:
            return
        connection = connections[self.db]
        return connection.runQuery(sql, params)