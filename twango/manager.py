from django.db import models
from twango.query import TwistedQuerySet

class TwistedManager(models.Manager):
    queryset_class = TwistedQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
