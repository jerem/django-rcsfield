"""
Dummy backend for django-rcsfield.

Django uses this if the RCS_BACKEND setting is empty (None or empty string).

Raises ImproperlyConfigured on all actions.
"""

from django.core.exceptions import ImproperlyConfigured


class DummyBackend(object):
    def _complain(self):
        raise ImproperlyConfigured, "You haven't set the RCS_BACKEND settings yet."
    
    def fetch(self, *args, **kwargs):
        return self._complain()
        
    def commit(self, *args, **kwargs):
        return self._complain()
    
    def initial(self, *args, **kwargs):
        return self._complain()
    
    def get_revisions(self, *args, **kwargs):
        return self._complain()
    
    def diff(self, *args, **kwargs):
        return self._complain()

rcs = DummyBackend()
