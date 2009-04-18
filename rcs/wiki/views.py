#based on protowiki written by Paul Bissex, MIT licensed.
#see e-scribe.com for more information
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django import template
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.utils.encoding import force_unicode
from rcs.wiki.models import WikiPage
from rcs.wiki.forms import UploadForm
from rcs.wiki.lock import EditLock, AlreadyLocked


def recent(request):
    '''show the last modified pages'''
    last = WikiPage.objects.all().order_by('-last_mod')[:5]
    return render_to_response('wiki/recent.html', locals(), context_instance=RequestContext(request))


    
def index(request):
    '''look for a WikiIndex page, otherwise return
       the first page found, if no page exists
       redirect to the edit view to create one'''
    try:
        page = WikiPage.objects.get(slug__exact='WikiIndex')
    except:
        try:
            page = WikiPage.objects.all()[0]
        except:
            return HttpResponseRedirect('/wiki/WikiIndex/edit/')
    return HttpResponseRedirect('/wiki/%s/' % page.slug)



def page(request, slug):
    """Display page, or redirect to create/edit if page doesn't exist yet"""
    rev = 'head'
    try:
        page = WikiPage.objects.get(slug__exact=slug)
        if request.GET.has_key('plain'):
            return HttpResponse(page.content, content_type="text/plain; charset=utf-8")
        return render_to_response('wiki/page.html', locals(), context_instance=RequestContext(request))
    except WikiPage.DoesNotExist:
        if request.user.is_authenticated():
            return HttpResponseRedirect("/wiki/%s/edit/" % slug)
        raise Http404
#page = cache_page(page, 60*60) #decorator doesn't work


        
@login_required
def edit(request, slug):
    """Process submitted page edits (POST) or display editing form (GET)"""
    
    try:
        lock = EditLock(slug, 60*15, request.user)
    except AlreadyLocked, e:
        # already locked by: e.lock_obj[0].username
        lock = None
    
    if request.POST:
        try:
            page = WikiPage.objects.get(slug__exact=slug)
        except WikiPage.DoesNotExist:
            # Must be a new one; let's create it
            page = WikiPage(slug=slug)
        page.content = request.POST['content']
        page.title = slug
        if request.POST.has_key('preview') and request.POST['preview']:
            return render_to_response('wiki/edit.html', dict(locals(), preview=True), context_instance=RequestContext(request))
        page.mod_by = request.user
        page.save()
        # release the edit lock, if we had one
        if lock is not None:
            lock.release()
        request.session['purge'] = page.slug
        return HttpResponseRedirect("/wiki/%s/" % page.slug)
    else:
        try:
            page = WikiPage.objects.get(slug__exact=slug)
        except WikiPage.DoesNotExist:
            # create a dummy page object -- note that it is not saved!
            page = WikiPage(slug=slug)
            page.content = "<!-- Enter content here -->"
        return render_to_response('wiki/edit.html', locals(), context_instance=RequestContext(request))



def list(request):
    '''list all wiki pages'''
    pages = WikiPage.objects.all().order_by('slug')
    return render_to_response('wiki/list.html', locals(), context_instance=RequestContext(request))



def revision(request, slug, rev):
    try:
        page = WikiPage.objects.rev(rev).get(slug__exact=slug)
    except:
        raise Http404
    if request.GET.has_key('plain'):
        return HttpResponse(page.content, content_type="text/plain; charset=utf-8")
    return render_to_response('wiki/page.html', locals(), context_instance=RequestContext(request))


    
def diff(request, slug, rev_a, rev_b):
    page = get_object_or_404(WikiPage, slug__exact=slug)
    rev = WikiPage.objects.rev(rev_b).get(slug=slug)
    diff = rev.get_content_diff(rev_a)
    x = u".. sourcecode:: diff\n\t\n"
    for line in diff:
        x = x + u"\t" + force_unicode(line)
    x = x + u"\n\n"
    return render_to_response('wiki/diff.html', locals(), context_instance=RequestContext(request))

def attachments(request, slug, form_class=UploadForm):
    page = get_object_or_404(WikiPage, slug__exact=slug)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.page = page
            attachment.save()
            return HttpResponseRedirect('.')
    else:
        form = form_class()
    attachments = page.wikiattachment_set.all()
    return render_to_response('wiki/attachments.html', locals(), context_instance=RequestContext(request))
    