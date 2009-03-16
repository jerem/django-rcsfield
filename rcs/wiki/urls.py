from django.conf.urls.defaults import *

urlpatterns = patterns('rcs.wiki.views',
    url(r'^((?:[A-Z]+[a-z]+){2,})/$', 'page', {}, name="wiki_page"),
    url(r'^((?:[A-Z]+[a-z]+){2,})/edit/$', 'edit', {}, name="wiki_edit"),
    url(r'^((?:[A-Z]+[a-z]+){2,})/attachments/$', 'attachments', {}, name="wiki_attachments"),
    url(r'^((?:[A-Z]+[a-z]+){2,})/rev/([0-9]+)/$', 'revision', {}, name="wiki_revision"),
    url(r'^((?:[A-Z]+[a-z]+){2,})/diff/([\w]+)/([\w]+)/$', 'diff', {}, name="wiki_diff"),
    url(r'^list/$', 'list', {}, name="wiki_list"),
    url(r'^recent/$', 'recent', {}, name="wiki_recent"),
    url(r'^$', 'index', {}, name="wiki_index"),
)