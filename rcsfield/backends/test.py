"""
Test backend for django-rcsfield.
"""

# importing like this needs a django settings.py:
#from rcsfield.backends.base import BaseBackend 
# this works without if we just want to run the doctests in this file:
from base import BaseBackend 

class NoSuchRevision(Exception):
    pass
    
    
class VersionizedDict(dict):
    """
    A dict which will hold a list for every key. 
    
    >>> d = VersionizedDict()
    >>> d['a'] = 'Hallo'
    >>> d['a'] = 'Hallo Welt'
    >>> d['a'] = 'Hallo Welt!'
    >>> d['B'] = [1,2,3]
    >>> d['B'] = [1,2]
    >>> d['B'] = [1]
    >>> d
    <VersionizedDict at rev 6 with keys: ['a', 'B']>
    >>> d['a']
    'Hallo Welt!'
    >>> d['B']
    [1]
    >>> d.get('a')
    'Hallo Welt!'
    >>> d.get('a', rev=6)
    'Hallo Welt!'
    >>> d.get('a', rev=5)
    'Hallo Welt!'
    >>> d.get('a', rev=2)
    'Hallo Welt'
    >>> d.get('a', rev=0)
    >>> d.get('B', rev=0)
    >>> d.get('B', rev=1)
    Traceback (most recent call last):
    ...
    NoSuchRevision
    >>> d.get('B', rev=1, default='X')
    'X'
    >>> d.get_revs_for_key('a')
    [1, 2, 3]
    >>> d.get_revs_for_key('B')
    [4, 5, 6]
    """
    def __init__(self, data=()):
        self.rev = 0
        self.history = []
        super(VersionizedDict, self).__init__(data)
        
    def __repr__(self):
        return "<%s at rev %s with keys: %s>" % (self.__class__.__name__,
                            self.rev, self.keys())
                            
    def __getitem__(self, key):
        list_ = super(VersionizedDict, self).__getitem__(key)
        try:
            return list_[0]
        except IndexError:
            return None
            
    def __setitem__(self, key, value):
        try:
            list_ = super(VersionizedDict, self).__getitem__(key)
            list_.insert(0, value)
        except KeyError:
            list_ = [value,]
        self.rev += 1
        self.history.append({'key': key, 'index': len(list_)-1})
        assert len(self.history) == self.rev
        return super(VersionizedDict, self).__setitem__(key, list_)
        
    def get(self, key, default=None, rev=None):
        if rev is None:
            return self.__getitem__(key)
        elif rev is 0:
            return default
        else:
            if rev > self.rev:
                raise NoSuchRevision
                
            list_ = super(VersionizedDict, self).__getitem__(key)
            try:
                changes = reversed(self.history[:rev])
                for change in changes:
                    if change['key'] == key:
                        try:
                            return list(reversed(list_))[change['index']]
                        except IndexError:
                            raise NoSuchRevision
            except IndexError:
                raise NoSuchRevision
            
            if default is not None:
                return default
            raise NoSuchRevision

    def get_revs_for_key(self, key):
        return [i+1 for i,v in enumerate(self.history) if v['key'] == key]

                

class TestBackend(BaseBackend):
    """
    Rcsfield backend used for testing.

    """

    def initial(self, prefix):
        """
        Set up a testrepo
        """
        self.repo = VersionizedDict()


    def fetch(self, key, rev):
        """
        fetch revision ``rev`` of entity identified by ``key``.

        """
        return self.repo.get(key, rev=rev)


    def commit(self, key, data):
        """
        commit changed ``data`` to the entity identified by ``key``.

        """
        try:
            old = self.repo[key]
        except KeyError:
            old = ''
        if data != old:
            self.repo[key] = data

        
    def get_revisions(self, key):
        """
        returns a list with all revisions at which ``key`` was changed.
        Revision Numbers are integers starting at 1.

        """
        return self.repo.get_revs_for_key(key)


    def move(self, key_from, key_to):
        raise NotImplementedError, "The test-backend doesn't allow moving of keys"




rcs = TestBackend()

fetch = rcs.fetch
commit = rcs.commit
initial = rcs.initial
get_revisions = rcs.get_revisions
diff = rcs.diff

__all__ = ('fetch', 'commit', 'initial', 'get_revisions', 'diff')

if __name__ == '__main__':
    import doctest
    doctest.testmod()   
    