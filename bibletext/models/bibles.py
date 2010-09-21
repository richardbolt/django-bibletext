from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

import bible # python-bible module. See http://github.com/jasford/python-bible

from fields import VerseField


class BibleBase(object):
    " Base class from which Bible, Book, and Verse implement. "
    
    def __str__(self):
        if hasattr(self, '__unicode__'):
            return force_unicode(self).encode('utf-8')
        return '%s object' % self.__class__.__name__
    
    def __iter__(self):
        for i in xrange(len(self)):
            yield self._get_element(i)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __le__(self, other):
        if (self.__lt__(other) or self.__eq__(other)):
            return True

        return False
    
    def __gt__(self, other):
        return not self.__le__()

    def __ge__(self, other):
        return not self.__lt__()


class Bible(BibleBase):
    " Represents a Bible (version/translation.) "
    def __init__(self, name, translation, book_data=None):
        self.name = name
        self.translation = translation # Letter code, eg: 'KJV'
        self._books = [] # Populate with self._set_books(book_data)

        if book_data:
            self.set_books(book_data)

        # Other natively supported parameters: TODO.
        self._introduction = None   # Use Markdown
        self._preface = None        # Use Markdown
        self._title_page = None     # Use Markdown


    def set_books(self, book_data):
        """
        Set the books, based on the given book_data.

        @args::

            `book_data`: list of dictionaries eg:
                [{
                    'testament': 'NT',
                    'verse_counts': [25, 25, 22, 19, 14],
                    'name': '1 Peter',
                    'abbrs': ['1pet', '1p', '1pe', '1 pe', '1pt', '1pe', '1 pet', '1 pt', '1 pe'],
                    'altname': 'The First Epistle General of Peter',
                },...]

        """
        book_num = 1
        for data in book_data:
            self._books.append(Book(self, number=book_num, **data))
            book_num += 1

    @property
    def num_books(self):
        return len(self._books)

    def __unicode__(self):
        return self.translation

    def __repr__(self):
        return u'<Bible: %s>' % self.translation

    def __len__(self):
        " Returns the number of books (66) in this Bible. "
        return self.num_books

    def __getitem__(self, key):
        " Get a specific book of the bible. NB: Slices and negative indexes are supported. "
        if not isinstance(key, (slice, int, long)):
            raise TypeError

        if isinstance(key, slice):
            (start, end, step) = key.indices(len(self)+1)
            if start == 0:
                raise IndexError
            if start in range(1, len(self._books)+1):
                start -= 1
            if end in range(len(self._books)+1):
                end -= 1
            return self._books[start:end:step]

        if key in range(1, len(self._books)+1): # key is the logical book number (1-66).
            return self._books[key-1]
        elif key in range(-len(self._books)-1, 0): # Negative index.
            return self._books[key]
        else:
            raise IndexError

    def __eq__(self, other):
        if type(self) == type(other):
            return self.translation == other.translation

        return False

    # Other rich comparators are explicitly NotImplemented on the Bible itself.
    def __lt__(self, other):
        raise NotImplemented

    def __le__(self, other):
        raise NotImplemented

    def __gt__(self, other):
        raise NotImplemented

    def __ge__(self, other):
        raise NotImplemented


class Book(BibleBase):
    " Book object. Represents a book of the Bible. "
    def __init__(self, bible=None, testament=None, number=None, name=None, abbreviations=None, verse_counts=None,
                omissions=None, altname=None, chapter_text=None):
        """
        Book __init__.

        @args::

            `bible`: The bible object that this book belongs to.

            `testament`: NT or OT.

            `number`: (int) Book number (starting from 1).

            `name`: The name of the book.

            `abbreviations`: List of abbreviations for the book name.

            `verse_counts`: (6, 10, ... ) list of list of verse counts (per chapter), all integers.

            `altname`: A long form name of this book. eg: "The gospel according to St John". Defaults to None.

            `omissions`: {12: [4,6,9, ...], ... } A mapping of chapter to lists of verse numbers that are omitted.

        """
        self.bible = bible
        self.textament = testament
        self.number = number # int(book number)
        self.name = name
        self.abbreviations = abbreviations
        self._chapters = []
        chapter_num = 1
        for verse_count in verse_counts:
            #print chapter_num, verse_count, type(verse_count)
            verse_list = range(1, verse_count+1)
            verse_omissions = None
            if omissions and chapter_num in omissions:
                verse_omissions = omissions[chapter_num]
            self._chapters.append(Chapter(self, chapter_num, verse_list, omissions=verse_omissions, chapter_text=chapter_text))
            chapter_num += 1
        self.num_chapters = len(self._chapters)
        self.altname = altname

    def __unicode__(self):
        return self.name

    def __len__(self):
        " Return the number of chapters. "
        return len(self._chapters)
    
    @property
    def num_verses(self):
        num = 0
        for chapter in self[:len(self)]:
            num += len(chapter)
        return num
    
    def _get_element(self, i):
        assert 0 <= i < len(self)
        return self._chapters[i]
    
    def __getitem__(self, key):
         " Get a specific chapter of this book. NB: Slices and negative indexes are supported. "
         if not isinstance(key, (slice, int, long)):
             raise TypeError

         if isinstance(key, slice):
             (start, end, step) = key.indices(len(self)+1)
             if start == 0:
                 raise IndexError
             if start in range(1, len(self._chapters)+1):
                 start -= 1
             if end in range(len(self._chapters)+1):
                 end -= 1
             return self._chapters[start:end:step]

         if key in range(1, len(self._chapters)+1): # key is the logical chapter number.
             return self._chapters[key-1]
         elif key in range(-len(self._chapters)-1, 0): # Negative index.
             return self._chapters[key]
         else:
             raise IndexError

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.bible, self.number) == (other.bible, other.number)

        return False

    def __lt__(self, other):
        if type(self) == type(other):
            if self.number == other.number:
                return self.number < other.number

        return False


class Chapter(BibleBase):
    """
    Chapter object. Represents a chapter in a book of the Bible.

    @args::
        `book`: :models:`bibletext.Book` that this chapter belongs to.

        `number`: int chapter number.

        `verses`: List of the verse numbers present in this Chapter.

        `chapter_text`: Defaults to `_('Chapter %d')`, and `_('Psalm %d')` for Psalms.

    """
    def __init__(self, book, number, verses, omissions=None, chapter_text=None):
        
        self.book = book # Needs to know the book we're in for comparators to operate.
        self.number = number # int(chapter number)
        if chapter_text:
            self.chapter_text = chapter_text
        elif self.book.number == 19: # Psalms are Psalms, not Chapters.
            self.chapter_text = _('Psalm %d')
        else:
            self.chapter_text = _('Chapter %d')
        self.name = self.chapter_text % self.number
        self._verses = []
        for verse in verses:
            self._verses.append(Verse(self, verse)) # NB: verse is the Verse number.
        self.num_verses = len(self._verses)

    def __unicode__(self):
        if len(self.book) == 1: # Only one chapter to the book, omit the chapter.
            return self.book

        return u'%s %s' % (self.book, self.number)

    def __len__(self):
        " Return the number of verses. "
        return self.num_verses
    
    def _get_element(self, i):
        assert 0 <= i < len(self)
        return self._verses[i]
    
    def __getitem__(self, key):
         " Get a specific verse of this chapter. NB: Slices and negative indexes are supported. "
         if not isinstance(key, (slice, int, long)):
             raise TypeError

         if isinstance(key, slice):
             (start, end, step) = key.indices(len(self)+1)
             if start == 0:
                 raise IndexError
             if start in range(1, len(self._verses)+1):
                 start -= 1
             if end in range(len(self._verses)+1):
                 end -= 1
             return self._verses[start:end:step]

         if key in range(1, len(self._verses)+1): # key is the logical verse number.
             return self._verses[key-1]
         elif key in range(-len(self._verses)-1, 0): # Negative index.
             return self._verses[key]
         else:
             raise IndexError

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.book, self.number) == (other.book, other.number)

        return False

    def __lt__(self, other):
        if type(self) == type(other):
            if self.bible == other.bible:
                if self.book < other.book or (self.book == other.book and self.number < other.number):
                    return True

        return False

    def __le__(self, other):
        if (self.__lt__(other) or self.__eq__(other)):
            return True

        return False


class Verse(BibleBase):
    """
    Verse object - this is used for formatting purposes.

    Also links in with the VerseText implementation.

    @args::

        `chapter`: The chapter object that this Verse belongs to.

        `number`: int verse number.

    """
    def __init__(self, chapter, number):
        self.chapter = chapter
        self.number = number
        if len(self.chapter.book) > 1:
            self.name = u'%s:%s' % (self.chapter.number, self.number)
        else: # Books with one chapter.
            self.name = unicode(self.number)
    
    def __unicode__(self):
        return u'%s %s' % (self.chapter.book, self.name)
    
    def __eq__(self, other):
        if type(self) == type(other):
            return (self.chapter, self.number) == (other.chapter, other.number)

        return False
    
    def __lt__(self, other):
        if type(self) == type(other):
            if self.bible == other.bible:
                if self.book < other.book or self.chapter < other.chapter or \
                        (self.book == other.book and self.chapter == other.chapter and
                                    self.number < other.number):
                    return True

        return False


class BiblePassageManager(models.Manager):
    " NB: verse and passage work with English at present. "
    
    def verse(self, reference):
        " Takes textual verse information and returns the Verse. "
        if self.model.translation and reference[-3] != self.model.translation:
            reference += ' '+self.model.translation
        verse = bible.Verse(reference)
        return self.get_query_set().get(book_id=verse.book.number, chapter_id=verse.chapter.number, verse_id=verse.number)
    
    def passage(self, start_reference, end_reference=None):
        """
        Takes textual passage information and returns the Verse(s).
        Note: you can't just input 'Romans 1:1-2:3',
        you'll need to do ('Romans 1:1', 'Romans 2:3') for the time being.
        """
        if not end_reference: # Probably just a single verse, return a list anyway.
            end_reference = start_reference
        
        if self.model.translation and start_reference[-3] != self.model.translation:
            start_reference += ' '+self.model.translation
        if self.model.translation and end_reference[-3] != self.model.translation:
            end_reference += ' '+self.model.translation
        
        # NB: len(passage) gives us the number of Verses in the passage.
        passage = bible.Passage(start_reference, end_reference)
        # We'll get the number of verses from the start like so to save a db lookup:
        in_the_beginning = 'Genesis 1:1'
        if self.model.translation:
            in_the_beginning += ' '+self.model.translation
        start_pk = len(bible.Passage(in_the_beginning, start_reference))
        return self.get_query_set().order_by('id').filter(pk__gte = start_pk)[:len(passage)]


class VerseText(models.Model):
    """
    VerseText (Bible) model - implement this abstract class for translations/versions.
    Each record (object) will be a single verse.
    """
    book_id = models.PositiveIntegerField(default=1)
    chapter_id = models.PositiveIntegerField(default=1)
    verse_id = models.PositiveIntegerField(default=1)
    
    text = models.TextField()
    
    translation = None # Use the translation code (KJV, NKJV etc) here according to what python-bible supports.    
    bible = None # Must implement Bible() to get formattable chapters, and so forth.
    
    objects = BiblePassageManager()
    
    def __unicode__(self):
        return u'%s %s:%s' % (self.book, self.chapter.number, self.verse.number)    
    
    class Meta:
        ordering = ('id') # Should already be: ('book_id', 'chapter_id', 'verse_id')
        unique_together = [('book_id', 'chapter_id', 'verse_id')]
        app_label = 'bibletext'
        abstract = True
    
    @classmethod
    def register_version(cls, *versions):
        """
        Register a list of bible versions::

            VerseText.register_version(
                KJV,
                )
        
        You can call this function as often as you like to register more bible versions.
        """
        if not hasattr(cls, 'versions'):
            cls.versions = []
        
        for version in versions:
            version_content_type = ContentType.objects.get_for_model(version)
            if version_content_type.pk not in cls.versions:
                cls.versions.append(version_content_type.pk)
    
    @property
    def book(self):
        return self.bible[self.book_id]
    
    @property
    def chapter(self):
        return self.book[self.chapter_id]
    
    @property
    def verse(self):
        return self.chapter[self.verse_id]
    
    @models.permalink
    def get_absolute_url(self):
        return ('bibletext_verse_detail', (), {
            'version':self.translation,
            'book_id': self.book.number,
            'chapter': self.chapter,
            'verse': self.verse})
    
    @models.permalink
    def get_chapter_url(self):
        return ('bibletext_chapter_detail', (), {
            'version':self.translation,
            'book_id': self.book.number,
            'chapter': self.chapter})
    
    #---------------------
    # Next/Previous Verses
    
    @property
    def next_verse(self):
        if hasattr(self, '_next_verse'):
            return self._next_verse
        try:
            self._next_verse = self.__class__.objects.get(pk=self.pk+1)
            return self._next_verse
        except self.__class__.DoesNotExist:
            self._next_verse = None
            return self._next_verse
    
    @property
    def prev_verse(self):
        if hasattr(self, '_prev_verse'):
            return self._prev_verse
        if self.book_id == 1 and self.chapter_id == 1 and self.verse_id == 1:
            self._prev_verse = None # Genesis 1:1 has no previous verse.
            return self._prev_verse
        self._prev_verse = self.__class__.objects.get(pk=self.pk-1)
        return self._prev_verse
    
    #-----------------------
    # Next/Previous Chapters
    
    @property
    def next_chapter(self):
        if hasattr(self, '_next_chapter'):
            return self._next_chapter
        if self.book_id == 66 and self.chapter_id == 22: # Nothing after Revelation 22...
            return None
                
        try:
            self.book[self.chapter.number + 1] # Next chapter in the same book...
            self._next_chapter = self.__class__.objects.get(book_id=self.book_id, chapter_id=self.chapter_id + 1, verse_id=1)
        except IndexError:
            # We'll be in the next book.
            self._next_chapter = self.__class__.objects.get(book_id=self.next_book_pk, chapter_id=1, verse_id=1)
        
        return self._next_chapter
    
    @property
    def prev_chapter(self):
        if hasattr(self, '_prev_chapter'):
            return self._prev_chapter
        if self.book_id == 1 and self.chapter_id == 1: # Nothing before Genesis 1...
            return None
        
        book_data = bible.data.bible_data(self.translation)[self.book_id-1] # NB: data is 0 indexed.
        
        if self.chapter_id - 1 <= 0: # We'll be in the previous book.
            chapter_id = self.bible[self.book-1][-1].number
            self._prev_chapter = self.__class__.objects.get(book_id=self.prev_book_pk, chapter_id=chapter_id, verse_id=1)
        else:
            self.book[self.chapter-1] # Previous chapter in the same book...
            self._prev_chapter = self.__class__.objects.get(book_id=self.book_id, chapter=self.chapter_id - 1, verse_id=1)
        
        return self._prev_chapter
    
    #---------------------
    # Next/Previous Books
    
    @property
    def next_book_pk(self):
        next_book_pk = self.book_id + 1
        if next_book_pk <= 66:
            return next_book_pk
        return None
    
    @property
    def prev_book_pk(self):
        prev_book_pk = self.book_id - 1
        if prev_book_pk > 0:
            return prev_book_pk
        return None
    
    @property
    def next_book(self):
        if self.next_book_pk:
            return self.bible[self.next_book_pk]
        return None
    
    @property
    def prev_book(self):
        if self.prev_book_pk:
            return self.bible[self.prev_book_pk]
        return None

