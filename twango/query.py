from django.db.models.query import QuerySet
from django.db.models.sql.query import Query
from twango.db import connections
from twango.decorators import call_in_thread


class TwistedQuery(Query):
    def twisted_compiler(self, using=None, connection=None):
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
        self.success_callback = None
        self.error_callback = None

    def twist(self):
        """
        Use twisted database api to run the query and return the raw results in a deferred
        """
        query = self.query
        assert(isinstance(query, Query))
        compiler = query.get_compiler(self.db)
        sql, params = compiler.as_nested_sql()
        if not sql:
            return
        connection = connections[self.db]
        return connection.runQuery(sql, params)

    def _super_threaded(self, name, *args, **kwargs):
        success_callback = kwargs.pop('success_callback', self.success_callback)
        error_callback = kwargs.pop('error_callback', self.error_callback)
        if not success_callback:
            raise ValueError('You must specify a success_callback')
        @call_in_thread(success_callback, error_callback)
        def function():
            getattr(super(TwistedQuerySet, self), name)(*args, **kwargs)
        return function()

    def _clone(self, klass=None, setup=False, **kwargs):
        self.success_callback = kwargs.pop('success_callback', self.success_callback)
        self.error_callback = kwargs.pop('error_callback', self.error_callback)
        clone = super(TwistedQuerySet, self)._clone(klass, setup, **kwargs)
        return clone

    def all(self, **kwargs):
        return self._super_threaded('all', **kwargs)

    def count(self, **kwargs):
        return self._super_threaded('count', **kwargs)

    def get(self, *args, **kwargs):
        return self._super_threaded('get', *args, **kwargs)

    def get_or_create(self, **kwargs):
        return self._super_threaded('get_or_create', **kwargs)

    def delete(self, **kwargs):
        return self._super_threaded('delete', **kwargs)

    def update(self, values, **kwargs):
        return self._super_threaded('update', values, **kwargs)


    def in_bulk(self, id_list, **kwargs):
        return self._super_threaded('in_bulk', id_list, **kwargs)