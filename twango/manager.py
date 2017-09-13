from django.db import models
from django.db.models import manager
from twango.query import TwistedQuerySet
from twisted.internet import threads

class TwistedManager(manager.BaseManager.from_queryset(TwistedQuerySet)):
    queryset_class = TwistedQuerySet
    _queryset_class = TwistedQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db, hints=self._hints)

    def all(self):
        return threads.deferToThread(lambda: super(TwistedManager, self).all())