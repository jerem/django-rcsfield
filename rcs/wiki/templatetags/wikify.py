# from http://open.e-scribe.com/browser/python/django/apps/protowiki/templatetags/wikitags.py
# copyright Paul Bissex, MIT license
from django.template import Library
from django.conf import settings
from rcs.wiki.models import WikiPage

register = Library()

@register.filter
def wikify(value):
    """Makes WikiWords"""
    import re
    #wikifier = re.compile(r'\b(([A-Z]+[a-z]+){2,})\b')
    def replace_wikiword(m):
        slug = m.group(1)
        try:
            WikiPage.objects.get(slug=slug)
            return r' <a href="/wiki/%s/">%s</a>' % (slug, slug)
        except WikiPage.DoesNotExist:
            return r' <a class="doesnotexist" href="/wiki/%s/">%s</a>' % (slug, slug)
        
    wikifier = re.compile(r'[^;/+-]\b(([A-Z]+[a-z]+){2,})\b')
    return wikifier.sub(replace_wikiword, value)