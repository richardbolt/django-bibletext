from django.core.xheaders import populate_xheaders
from django.core.paginator import Paginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.template import loader, RequestContext

from bible import Verse, RangeError, book_re # python-bible module.
from bible.data import bible_data

from models import Scripture, Book, KJV
from utils import lookup_translation


def chapter(request, book_id, chapter, version=KJV, template_name=None, template_name_field=None,
        template_loader=loader, extra_context=None, context_processors=None,
        template_object_name='verse_list', mimetype=None):
    """
    Renders an entire chapter based on the given book and chapter.
    
    @args::
        
        `book_id`: (int) Pk of the Book to be used.
        
        `chapter`: (int) The chapter to render.
        
        `bible`: The Bible version to be used.
    
    """
    if extra_context is None: extra_context = {}
    
    if not book_id and chapter:
        raise AttributeError("Chapter detail view must be called with a book_id and a chapter.")
    
    if type(version) in (str, unicode):
        bible = lookup_translation(version)
    else:
        bible = version # Perhaps we were sent a VerseText implementation like the KJV.
    
    book = Book.objects.get(pk=book_id)
    
    try:
        verse_list = bible.objects.filter(book__pk=book_id, chapter=chapter)
    except bible.DoesNotExist:
        raise Http404("Chapter not found in the given book of %s." % bible.translation)
    
    if not template_name:
        template_name = "bibletext/chapter_detail.html"
    if template_name_field:
        template_name_list = [getattr(obj, template_name_field), template_name]
        t = template_loader.select_template(template_name_list)
    else:
        t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        template_object_name: verse_list,
        'book': book,
        'chapter': chapter,
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