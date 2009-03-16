try:
    import pygments
    from rcs.wiki.lib import pygments_rest
except ImportError:
    pass
    # don't import the pygments rest directive if pygments is not installed.
    
from django import template
from django.conf import settings

register = template.Library()

def restructuredtext(value):
    try:
        from docutils.core import publish_parts
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError, "Error in {% restructuredtext %} filter: The Python docutils library isn't installed."
        return value
    else:
        docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
        parts = publish_parts(source=value, writer_name="html4css1", settings_overrides=docutils_settings)
        return parts["html_body"]

register.filter(restructuredtext)    