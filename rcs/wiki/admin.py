from django.contrib import admin
from rcs.wiki.models import WikiPage, WikiAttachment

admin.site.register(WikiPage)
admin.site.register(WikiAttachment)