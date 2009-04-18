from datetime import datetime
from django.core.cache import cache
from django.conf import settings


class AlreadyLocked(Exception):
    def __init__(self, lock):
        self.lock_obj = lock
        super(AlreadyLocked, self).__init__()


class EditLock(object):
    """
    Using Django's cache system this class implements edit-locking for
    Wiki pages.
    To aquire a lock just instantiate a ``EditLock`` object. If a lock
    for the resource at ``slug`` already exists an AlreadyLocked exception
    is raised, which provides access to the lock via ``lock_obj`` attribute.
    To release a lock call the release() method on the lock object.
    ``duration`` is the lock period in seconds.
    The lock itself holds a tuple containing the ``owner`` and the creation
    time.
    """
    def __init__(self, slug, duration, owner, cache_key_prefix=u"rcs.wiki:editlock"):
        self.cache_key = "%s%s:%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, 
                                      cache_key_prefix, slug)
        
        lock = cache.get(self.cache_key)
        if lock is not None:
            # not locked by ourself?
            if lock[0] != owner: 
                raise AlreadyLocked(lock)
        else:
            cache.set(self.cache_key, (owner, datetime.now()), duration)
        
    def release(self):
        cache.delete(self.cache_key)
