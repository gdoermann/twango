twango = Django ORM + Twisted - Blocking
----------------------------------------
This is a library that contains a custom queryset and a custom manager that adds introspection to use
the twisted database api instead of django.  It returns deferred instead of just hitting the database.

To install:
-----------
1. Run python setup.py
2. Import and set the manager as the manager for any model

This will keep the orm from blocking when using the django orm!

Important
-----------
Does not make job in asynchronous way, but goes into threads and do not perform blocking main reactor.


Example Updated:
--------

Returns defered.
Does any methods call except "all", eg: Book.twisted.all()
```python
d = Book.twisted.count()
d.addCallback(do_something)
```

Aslo "success_callback" and "error_callback" can be passed
```python
d = Book.twisted.count(success_callback=do_something)
d.addCallback(do_something2)
```

Calling "all" method similarly, returns defered but does not accept any arguments
```python
d = Book.twisted.all()
d.addCallback(do_something)
```


Example:
--------
You can create models that are separate to be used in twisted processes:

```python
from myapp import Book
from twango.manager import TwistedManager
from django.db.models.manager import Manager

class TwistedBook(Book):
    objects = Manager()
    twisted = TwistedManager()

    class Meta:
        app_label = 'myapp'
        proxy = True
```

Then you can use the twisted manager like you would with the regular manager... just with callbacks!

```python
def count_me(count):
    print "Count: %s" % count

def all(queryset):
    print 'All: %s' % queryset

def none(queryset):
    print 'None: %s' % queryset

def callback(*args, **kwargs):
    Book.twisted.count(success_callback=count_me)
    Book.twisted.all(success_callback=all)
    Book.twisted.none(success_callback=none)

d = Deferred()
d.addCallback(callback)
d.callback(None)

reactor.run()
```
