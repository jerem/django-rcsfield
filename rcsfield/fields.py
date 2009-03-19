import difflib
from django.db import models
from django.conf import settings
from django.db.models import signals, TextField
from django.utils.functional import curry
from django.utils import simplejson as json
from rcsfield.backends import backend
from rcsfield.widgets import RcsTextFieldWidget, JsonWidget



class RcsTextField(models.TextField):
    """
    save contents of the TextField in a revison control repository.
    The field has an optionl argument: ``rcskey_format``, the format-
    string to use for interpolating the key under which the content should
    be versionized.

    signal post_syncdb:
        do some optional repository initialization

    object added:
        the object is saved to the db, and commited to the repo
    object deleted:
        not implemented yet
    object changed:
        save changes to db and commit changes to repo

    the cool thing here is, that the ``head`` version is also
    saved in the db, this makes retrieval really fast. revison control
    backend is only used on save() and for retrieval of old revisions.

    """


    def __init__(self, *args, **kwargs):
        """
        Allow specifying a different format for the key used to identify
        versionized content in the model-definition.

        """
        #TODO: check if the string has the correct format
        self.rcskey_format = kwargs.pop('rcskey_format', "%s/%s/%s/%s.txt")
        self.IS_VERSIONED = True # so we can figure out that this field is versionized
        TextField.__init__(self, *args, **kwargs)


    def get_internal_type(self):
        return "TextField"

    def get_key(self, instance):
        format_args = (instance._meta.app_label,
                       instance.__class__.__name__,
                       self.attname,
                       instance.pk)
        return self.rcskey_format % format_args
        
    def post_save(self, instance=None, **kwargs):
        """
        create a file and add to the repository, if not already existing
        called via post_save signal

        """
        data = getattr(instance, self.attname)
        key = self.get_key(instance)
        backend.commit(key, data.encode('utf-8'))


    def get_changed_revisions(self, instance, field):
        """
        Returns all revisions at which some Rcs*Field on the model instance
        changed.
        
        """
        revs = []
        for field in instance._meta.fields:
            if hasattr(field, 'IS_VERSIONED') and field.IS_VERSIONED:
                revs.extend(field.get_FIELD_revisions(instance, field))
        return list(reversed(sorted(revs)))


    def get_FIELD_revisions(self, instance, field):
        return backend.get_revisions(self.get_key(instance))


    def get_FIELD_diff(self, instance, rev1, rev2=None, field=None):
        """
        Returns a generator which yields lines of a textual diff between
        two revisions.
        Supports two operation modes:

           ObjectA.get_field_diff(3): returns a diff between the contents of
           the field ``field`` at revision 3 against revision of ObjectA.
           Direction is ---3 / +++ObjectA

           ObjectA.get_field_diff(3,7): returns a diff between the contents of
           the field ``field`` at revision 7 against revision 3..
           Direction is ---3/+++7

        """


        if rev2 is None:
            rev2 = getattr(instance, '%s_revision' % field.attname, 'head')

        if rev1 == rev2: #do not attempt to diff identical content for performance reasons
            return ""

        key = self.get_key(instance)
        if rev2 == 'head':
            old = backend.fetch(key, rev1)
            diff = difflib.unified_diff(
                    old.splitlines(1),
                    getattr(instance, field.attname).splitlines(1),
                    'Revision: %s' % rev1,
                    'Revision: %s' % getattr(instance, "%s_revision" % field.attname, 'head'),
                   )
            return diff

        else: #diff two arbitrary revisions
            return backend.diff(key, rev1, key, rev2)

    def contribute_to_class(self, cls, name):
        super(RcsTextField, self).contribute_to_class(cls, name)
        setattr(cls, 'get_%s_revisions' % self.name, curry(self.get_FIELD_revisions, field=self))
        setattr(cls, 'get_changed_revisions', curry(self.get_changed_revisions, field=self))
        setattr(cls, 'get_%s_diff' % self.name, curry(self.get_FIELD_diff, field=self))
        signals.post_save.connect(self.post_save, sender=cls)




class RcsJsonField(RcsTextField):
    """
    Save arbitrary data structures serialized as json and versionize them.

    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value == "":
            return None
        if isinstance(value, basestring):
            return json.loads(value)
        return value


    def get_db_prep_save(self, value):
        if value is not None:
            if not isinstance(value, basestring):
                value = json.dumps(value)
        return models.TextField.get_db_prep_save(self, value)


    def formfield(self, **kwargs):
        defaults = {}
        defaults.update(kwargs)
        defaults.update({'widget': JsonWidget}) # needs to be here and not in the form-field because otherwise contrib.admin will override our widget
        return super(RcsJsonField, self).formfield(**defaults)

    def post_save(self, instance=None, **kwargs):
        """
        create a file and add to the repository, if not already existing
        called via post_save signal

        """
        data = getattr(instance, self.attname)
        key = self.get_key(instance)
        backend.commit(key, json.dumps(data)) #.decode().encode('utf-8'))
