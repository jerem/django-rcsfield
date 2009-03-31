"""
Mercurial backend for django-rcsfield.

"""

import os, codecs
from django.conf import settings
from mercurial import hg, ui, commands, localrepo, error
from rcsfield.backends.base import BaseBackend



class MercurialBackend(BaseBackend):
    """
    Rcsfield backend which uses mercurial to versionize content.

    """

    def __init__(self, location):
        self.location = os.path.normpath(location)
        self.hg_ui = ui.ui(interactive=False)

    def initial(self, prefix):
        """
        Set up the hg repo at ``self.location``, which usually
        is set in ``settings.HG_REPO_PATH``.

        """
        if not os.path.exists(self.location):
            os.makedirs(self.location)
        u = self.hg_ui
        try:
            repo = hg.repository(u, self.location, create=1)
        except error.RepoError:
            repo = hg.repository(u, self.location)
        except Exception, e:
            raise
 
        
    def fetch(self, key, rev):
        """
        fetch revision ``rev`` of entity identified by ``key``.
        FIXME: error handling?
        """
        u = self.hg_ui
        repo = hg.repository(u, self.location)
        
        try:
            fctx = repo[rev][key]
        except (error.RepoError, error.LookupError, IndexError):
            fctx = repo.filectx(key, fileid=rev)
    
        try:
            return fctx.data()
        except (error.LookupError, IndexError):
            return ''


    def commit(self, key, data):
        """
        commit changed ``data`` to the entity identified by ``key``.

        """

        try:
            fobj = open(os.path.join(self.location, key), 'w')
        except IOError:
            #parent directory seems to be missing
            os.makedirs(os.dirname(os.path.join(self.location, key)))
            return self.commit(key, data)
        fobj.write(data)
        fobj.close()
        
        u = self.hg_ui
        repo = hg.repository(u, self.location)
        try:
            commands.add(u, repo, os.path.join(self.location, key))
        except:
            raise
        commands.commit(u, repo, message='auto commit from django')


    def get_revisions(self, key):
        """
        returns a list with all revisions at which ``key`` was changed.
        Revision Numbers are integers starting at 0.
        Every ``key`` has its own revision numbers, other backends have
        global unique revision numbers.
        
        """
        u = self.hg_ui
        repo = hg.repository(u, self.location)
        f = repo.file(key)
        return list(f)[:-1]



    def move(self, key_from, key_to):
        """
        Moves an entity from ``key_from`` to ``key_to`` while keeping
        the history. This is useful to migrate a repository after the
        ``rcskey_format`` of a field was changed.
        TODO: move from mecurial.commands to internal api.#
        
        """
        u = self.hg_ui
        repo = hg.repository(u, self.location)
        absp = lambda p: os.path.join(self.location, p)
        try:
            commands.rename(u, repo, absp(key_from), absp(key_to))
            commands.commit(u, repo, message="Moved %s to %s" % (key_from, key_to))
            return True
        except:        
            return False





rcs = MercurialBackend(settings.HG_REPO_PATH)

fetch = rcs.fetch
commit = rcs.commit
initial = rcs.initial
get_revisions = rcs.get_revisions
move = rcs.move
diff = rcs.diff

__all__ = ('fetch', 'commit', 'initial', 'get_revisions', 'move', 'diff')
