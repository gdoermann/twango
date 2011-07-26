from django.db import models
from dwisted.query import TwistedQuerySet

class CustomManager(models.Manager):
    queryset_class = TwistedQuerySet

    def get_query_set(self):
        return self.queryset_class(self.model, using=self._db)
