# from http://open.e-scribe.com/browser/python/django/apps/protowiki/templatetags/wikitags.py
# copyright Paul Bissex, MIT license
from django.template import Library
from django.conf import settings

register = Library()

@register.filter
def wikify(value):
    """Makes WikiWords"""
    import re
    #wikifier = re.compile(r'\b(([A-Z]+[a-z]+){2,})\b')
    wikifier = re.compile(r'[^>;/+-]\b(([A-Z]+[a-z]+){2,})\b')
    return wikifier.sub(r' <a href="/wiki/\1/">\1</a>', value)