from django.db import models
from django.contrib.auth.models import User
from rcsfield.fields import RcsTextField
from rcsfield.manager import RevisionManager


class WikiPage(models.Model):
    slug = models.CharField(max_length=50)
    last_mod = models.DateTimeField(auto_now=True)
    mod_by = models.ForeignKey(User, null=True)
    content = RcsTextField()
    
    objects = RevisionManager()
    
    def __unicode__(self):
        return self.slug
    
    @models.permalink    
    def get_absolute_url(self):
        return "wiki_page", [self.slug,]