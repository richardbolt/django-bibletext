from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_save

import bible

from bibles import Book, VerseText, KJV
from fields import VerseField


# Collections of verses for use.
VerseText.register_version(KJV)

class Scripture(models.Model):
    "Scripture object to display the text of a passage (or verse) of scripture."
    start_verse = VerseField()
    end_verse = VerseField(blank=True, help_text="Leave blank for a single verse.")
    
    version = models.ForeignKey(ContentType, limit_choices_to={'pk__in': VerseText.versions})
    
    # For generic relations
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey("content_type", "object_id")
    
    # Auto-generated fields for sorting, filtering, etc:
    start_book = models.ForeignKey(Book, related_name='start_scriptures')
    start_chapter = models.PositiveIntegerField()
    start_verse_number = models.PositiveIntegerField()
    
    end_book = models.ForeignKey(Book, related_name='end_scriptures', blank=True, null=True)
    end_chapter = models.PositiveIntegerField(blank=True, null=True)
    end_verse_number = models.PositiveIntegerField(blank=True, null=True)
    
    def __unicode__(self):
        if self.end_verse:
            return bible.Passage(self.start_verse, self.end_verse).format()
        return self.start_verse
        
    class Meta:
        app_label = 'bibletext'
        ordering = ('start_book', 'start_chapter', 'start_verse_number')
    
    def get_passage(self):
        return self.version.model_class().objects.passage(self.start_verse, self.end_verse)    
    passage = property(get_passage)
    
    def get_verse(self):
        "Returns the start verse object."
        return self.version.model_class().objects.verse(self.start_verse)
    verse = property(get_verse)


def populate_scripture_details(sender, instance, **kwargs):
    start = bible.Verse(instance.start_verse)
    instance.start_book = Book.objects.get(pk=start.book)
    instance.start_chapter = start.chapter
    instance.start_verse_number = start.verse
    if instance.end_verse:
        end = bible.Verse(instance.end_verse)
        if start.book == end.book:
            instance.end_book = instance.start_book
        else:
            instance.end_book = Book.objects.get(pk=end.book)
        instance.end_chapter = end.chapter
        instance.end_verse_number = end.verse
pre_save.connect(populate_scripture_details, sender=Scripture)