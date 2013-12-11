"""
Unit Tests for django-bibletext.
"""

from django.test import TestCase

from bibletext.models import KJV


class KJVModels(TestCase):
    fixtures = ['kjv.json']
    
    def setUp(self):
        pass
    
    def length(self):
        " Tests length operations. "
        self.failUnlessEqual(KJV.bible.num_verses, KJV.objects.all().count())
        
