from django.contrib.contenttypes.models import ContentType
from django.core.xheaders import populate_xheaders
from django.core.paginator import Paginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext

from bible import Verse, RangeError, book_re # python-bible module.
from bible.data import bible_data

from models import Scripture, KJV, VerseText
from utils import lookup_translation


def bible_list(request, template_name=None, template_loader=loader, extra_context=None,
        context_processors=None, template_object_name='bible_list', mimetype=None):
    """
    Renders a list of the bible attributes from the registered VerseText implementations.
        
        NB: Don't forget to register a VerseText implementation like so:
        `VerseText.register_version(KJV)`.

    """
    if extra_context is None: extra_context = {}
    
    bible_list = []
    bible_content_types = ContentType.objects.filter(pk__in=VerseText.versions)
    for bible_content_type in bible_content_types:
        bible_list.append(bible_content_type.model_class().bible)
    
    if not template_name:
        template_name = "bibletext/bible_list.html"
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        template_object_name: bible_list,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)


def bible(request, version=KJV, template_name=None,
        template_loader=loader, extra_context=None, context_processors=None,
        template_object_name='bible', mimetype=None):
    """
    Renders a list of books for a given Bible.
    
    @args::
                        
        `version`: The Bible version to be used. You can use either the actual object or a string
        representing the translation attribute (eg: KJV or 'KJV')
    
    """
    if extra_context is None: extra_context = {}
    
    if type(version) in (str, unicode):
        bible = lookup_translation(version)
    else:
        bible = version # Perhaps we were sent a VerseText implementation like the KJV.
    
    bible = bible.bible # The Bible() object implementation.
    
    if not template_name:
        template_name = "bibletext/bible_detail.html"
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        template_object_name: bible,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)


def book(request, book_id, version=KJV, template_name=None,
        template_loader=loader, extra_context=None, context_processors=None,
        template_object_name='book', mimetype=None):
    """
    Renders a list of chapters for a given book.
    
    @args::
        
        `book_id`: (int) Pk of the Book to be used.
                
        `version`: The Bible version to be used. You can use either the actual object or a string
        representing the translation attribute (eg: KJV or 'KJV')
    
    """
    if extra_context is None: extra_context = {}
    
    if not book_id:
        raise AttributeError("Book detail view must be called with a book_id.")
    
    if type(version) in (str, unicode):
        bible = lookup_translation(version)
    else:
        bible = version # Perhaps we were sent a VerseText implementation like the KJV.
    
    book_id = int(book_id)
    
    try:
        book = bible.bible[book_id]
        chapter = bible.bible[book_id][1] # First chapter of the given book.
        verse_list = bible.objects.filter(book_id=book_id, chapter_id=1)
    except (IndexError, bible.DoesNotExist):
        raise Http404("Book not found in the %s." % bible.translation)
    
    if not template_name:
        template_name = "bibletext/book_detail.html"
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        template_object_name: book,
        'chapter': chapter,
        'verse_list': verse_list,
        'bible': bible,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)


def chapter(request, book_id, chapter_id, version=KJV, template_name=None,
        template_loader=loader, extra_context=None, context_processors=None,
        template_object_name='verse_list', mimetype=None):
    """
    Renders an entire chapter based on the given book and chapter.
    
    @args::
        
        `book_id`: (int) Pk of the Book to be used.
        
        `chapter_id`: (int) The chapter to render.
        
        `version`: The Bible version to be used. You can use either the actual object or a string
        representing the translation attribute (eg: KJV or 'KJV')
    
    """
    if extra_context is None: extra_context = {}
    
    if not (book_id or chapter_id):
        raise AttributeError("Chapter detail view must be called with a book_id and a chapter.")
    
    if type(version) in (str, unicode):
        bible = lookup_translation(version)
    else:
        bible = version # Perhaps we were sent a VerseText implementation like the KJV.
    
    book_id = int(book_id)
    chapter_id = int(chapter_id)
    
    try:
        chapter = bible.bible[book_id][chapter_id]
        verse_list = bible.objects.filter(book_id=book_id, chapter_id=chapter_id)
    except (IndexError, bible.DoesNotExist):
        raise Http404("Chapter not found in the given book of %s." % bible.translation)
    
    if not template_name:
        template_name = "bibletext/chapter_detail.html"
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        template_object_name: verse_list,
        'book': chapter.book,
        'chapter': chapter,
        'bible': bible,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)


def verse(request, book_id, chapter_id, verse_id, version=KJV, template_name=None,
        template_loader=loader, extra_context=None, context_processors=None,
        template_object_name='verse', mimetype=None):
    """
    Renders a single verse based on the given book, chapter, and verse.

    @args::

        `book_id`: (int) Pk of the Book to be used.

        `chapter`: (int) The chapter to render.

        `version`: The Bible version to be used.

    """
    if extra_context is None: extra_context = {}

    if not (book_id or chapter_id or verse_id):
        raise AttributeError("Verse detail view must be called with a book_id, chapter_id, and a verse_id.")

    if type(version) in (str, unicode):
        bible = lookup_translation(version)
    else:
        bible = version # Perhaps we were sent a VerseText implementation like the KJV.
    
    verse = get_object_or_404(bible, book_id=book_id, chapter_id=chapter_id, verse_id=verse_id)

    if not template_name:
        template_name = "bibletext/verse_detail.html"
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        template_object_name: verse,
        'book': verse.book,
        'chapter': verse.chapter,
        'bible': bible,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)



# TODO: Finish what I had started here. This is currently non-functional..
def passage_lookup(request, version, template_name=None, template_loader=loader,
        extra_context=None, context_processors=None, template_object_name='object',
        mimetype=None):
    """
    Given a textual passage via GET[q] displays the reference, or simply displays a
    passage entry form.
    
    @args::
        
        `version`: The translation to be used.
        
        GET[q]: `Romans 1:1-2:3`, or `Romans 1:1 - 1 Corinthians 2:3`, etc.
    
    """
    
    passage_reference = request.GET.get('q', False)
    if passage_reference:
        if '-' in passage_reference:
            ref = passage_reference.split('-') # Split the passage_reference into start and end verses.
            if len(ref) > 2:
                # Whoa, too many `-` characters...
                raise RangeError("We can't make sense of your chapter:verse passage reference.")
            start_verse = Verse(ref[0].strip())
            # Now the end verse. This could be in the same book, or a different book entirely.
            # eg: `Romans 1:1-2:3`, or `Romans 1:1 - 1 Corinthians 2:3`
            end_ref = ref[1].strip()
            
            # If we can't find the book reference, assume it is part of the same book.
            try:
                b = book_re.search(ref[1].strip()).group(0)
            except:
                # Assume the same book:
                end_ref = '%s ' % (bible_data()[start_verse.book]['name'], end_ref)
            
            end_verse = Verse(end_ref)
            
            
        else:
            start_verse = start_verse
            end_verse = None
    
        Scripture(start_verse=start_verse.format(), end_verse=end_verse)
    return HttpResponse