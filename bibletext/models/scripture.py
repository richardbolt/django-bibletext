from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_save

import bible # python-bible module.

from bibles import Book, VerseText
from kjv import KJV
from fields import VerseField


class Scripture(models.Model):
    "Scripture object to display the text of a passage (or verse) of scripture."
    start_verse = VerseField()
    end_verse = VerseField(blank=True, help_text="Leave blank for a single verse.")
    
    version = models.ForeignKey(ContentType, limit_choices_to={'pk__in': VerseText.versions}, related_name='bible_versions')
    
    # For generic relations
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey("content_type", "object_id")
    
    # Auto-generated fields for sorting, filtering, etc:
    start_book_id = models.PositiveIntegerField()
    start_chapter_id = models.PositiveIntegerField()
    start_verse_id = models.PositiveIntegerField()
    
    end_book_id = models.PositiveIntegerField(blank=True, null=True)
    end_chapter_id = models.PositiveIntegerField(blank=True, null=True)
    end_verse_id = models.PositiveIntegerField(blank=True, null=True)
    
    def __unicode__(self):
        if self.end_verse:
            return bible.Passage(self.start_verse, self.end_verse).format()
        return self.start_verse
        
    class Meta:
        app_label = 'bibletext'
        ordering = ('start_book_id', 'start_chapter_id', 'start_verse_id')
    
    @property
    def start_book(self):
        self.version.bible[self.start_book_id]
    
    @property
    def end_book(self):
        self.version.bible[self.end_book_id]
    
    def get_passage(self):
        return self.version.model_class().objects.passage(self.start_verse, self.end_verse)    
    passage = property(get_passage)
    
    def get_verse(self):
        "Returns the start verse object."
        return self.version.model_class().objects.verse(self.start_verse)
    verse = property(get_verse)


def populate_scripture_details(sender, instance, **kwargs):
    start = bible.Verse(instance.start_verse)
    instance.start_book_id = start.book_id
    instance.start_chapter_id = start.chapter_id
    instance.start_verse_id = start.verse_id
    if instance.end_verse:
        end = bible.Verse(instance.end_verse)
        if start.book == end.book:
            instance.end_book_id = instance.start_book_id
        else:
            instance.end_book_id = end.book.number
        instance.end_chapter_id = end.chapter_id
        instance.end_verse_id = end.verse_id
pre_save.connect(populate_scripture_details, sender=Scripture)