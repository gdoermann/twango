from django.db.models.query import QuerySet
from django.db.models.sql.query import Query
from twango.db import connections
from twango.decorators import call_in_thread


class TwistedQuery(Query):
    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        else:
            connection = connections[connection.alias]
        # Check that the compiler will be able to execute the query
        for alias, aggregate in self.aggregate_select.items():
            connection.ops.check_aggregate_support(aggregate)

        return connection.ops.compiler(self.compiler)(self, connection, using)


class TwistedQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None):
        query = query or TwistedQuery(model)
        super(TwistedQuerySet, self).__init__(model=model, query=query, using=using)

    def twisted(self):
        query = self.query
        assert(isinstance(query, Query))
        compiler = query.get_compiler(self.db)
        sql, params = compiler.as_nested_sql()
        if not sql:
            return
        connection = connections[self.db]
        return connection.runQuery(sql, params)

    @call_in_thread
    def count(self):
        #TODO: Make it twisted aware!
        return super(TwistedQuerySet, self).count()

    @call_in_thread
    def get(self, *args, **kwargs):
        #TODO: Make it twisted aware!
        return super(TwistedQuerySet, self).get(self, *args, **kwargs)

    @call_in_thread
    def get_or_create(self, **kwargs):
        return super(TwistedQuerySet, self).get_or_create(self, **kwargs)

    @call_in_thread
    def delete(self):
        return super(TwistedQuerySet, self).delete(self)