import itertools
from django.test import TestCase
from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rcsfield.fields import RcsTextField, RcsJsonField
from rcsfield.manager import RevisionManager


if 'test' not in settings.RCS_BACKEND:
    raise ImproperlyConfigured('only run rcsfield tests with the test-backend.')


TDATA = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do 
eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit 
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat 
cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est 
laborum."""

TDATA2 = " ".join(TDATA.split()[:10])
TDATA3 = " ".join(TDATA.split()[:20])


class TextModel(models.Model):
    text = RcsTextField()
    text2 = RcsTextField()
    objects = RevisionManager()
    
class JsonModel(models.Model):
    json = RcsJsonField()
    text2 = RcsTextField()
    objects = RevisionManager()


        
class TextFieldTestCase(TestCase):
    """
    Just assures that the RcsTextField will persist the (correct) data
    """
    def testContent(self):
        obj = TextModel.objects.create(text=TDATA)
        pk = obj.pk
        obj = TextModel.objects.get(pk=pk)
        self.assertEquals(TDATA, obj.text)
        obj.text = TDATA2
        obj.save()
        obj = TextModel.objects.get(pk=pk)
        self.assertEquals(TDATA2, obj.text)
        
class JsonFieldTestCase(TestCase):
    """
    Just assure that the RcsJsonField will persist the (correct) data.
    """
    def testContent(self):
        obj = JsonModel.objects.create(json=TDATA.split())
        pk = obj.pk
        obj = JsonModel.objects.get(pk=pk)
        self.assertEquals(TDATA.split(), obj.json)
        obj.json = TDATA2.split()
        obj.save()
        obj = JsonModel.objects.get(pk=pk)
        self.assertEquals(TDATA2.split(), obj.json)    


class RevisionAPITestCase(TestCase):
    def setUp(self):
        self.obj = TextModel.objects.create(text=TDATA)
        self.obj.text = TDATA2
        self.obj.save()
        self.obj.text = TDATA3
        self.obj.save()
    
    def testListing(self):
        self.assertEquals(self.obj.get_text_revisions(), [1,2,3])
        
    def testRetrieval(self):
        head = TextModel.objects.rev().get(pk=self.obj.pk)
        rev1 = TextModel.objects.rev(1).get(pk=self.obj.pk)
        rev2 = TextModel.objects.rev(2).get(pk=self.obj.pk)
        rev3 = TextModel.objects.rev(3).get(pk=self.obj.pk)

        self.assertEquals(head.text, TDATA3)
        self.assertEquals(rev1.text, TDATA)
        self.assertEquals(rev2.text, TDATA2)
        self.assertEquals(rev3.text, TDATA3)
        
    def testBulk(self):
        obj = TextModel()
        for word in TDATA.split():
            obj.text = word
            obj.save()
            
        revs = obj.get_text_revisions()
        
        self.assertEquals(len(revs), len(TDATA.split()))
        
        for rev, word in itertools.izip(revs, TDATA.split()):
            self.assertEquals(TextModel.objects.rev(rev).get(pk=obj.pk).text, word)
            
    def test_get_changed_revisions(self):
        self.assertEquals(self.obj.get_changed_revisions(), [1,2,3])
        self.assertEquals(self.obj.get_changed_revisions(), self.obj.get_text_revisions())
        
        
class TextMultipleObjectsOneRepo(TestCase):
    """
    Test that multiple models can committ to the same repo without mixing up.
    """
    def setUp(self):
        self.obj1 = TextModel.objects.create(text=TDATA2)
        self.obj2 = TextModel.objects.create(text=TDATA3)
    
    def testAlternation(self):
        self.obj1.text = TDATA3
        self.obj1.save()
        
        self.obj2.text = TDATA2
        self.obj2.save()
        
        obj1 = TextModel.objects.get(pk=self.obj1.pk)
        obj2 = TextModel.objects.get(pk=self.obj2.pk)
        self.assertEquals(obj1.text, TDATA3)
        self.assertEquals(obj2.text, TDATA2)
        
        self.assertEquals(obj1.get_text_revisions(), [1,3])
        self.assertEquals(obj2.get_text_revisions(), [2,4])
        self.assertEquals(obj1.get_changed_revisions(), obj1.get_text_revisions())
        self.assertEquals(obj2.get_changed_revisions(), obj2.get_text_revisions())
        
    def testMultipleFields(self):
        self.obj1.text = TDATA3
        self.obj1.save()
        self.obj1.text2 = TDATA2
        self.obj1.save()
        
        obj1 = TextModel.objects.get(pk=self.obj1.pk)
        self.assertEquals(obj1.get_text_revisions(), [1,3])
        self.assertEquals(obj1.get_text2_revisions(), [4])
        
        # this test fails as documented in issue #11
        # enable it after fixing the issue
        self.assertEquals(obj1.get_changed_revisions(), [1,3,4])

        
        
        