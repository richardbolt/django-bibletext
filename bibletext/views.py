from django.template import loader, RequestContext
from django.http import Http404, HttpResponse
from django.core.xheaders import populate_xheaders
from django.core.paginator import Paginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist

from bible import Verse, RangeError, book_re # python-bible
from bible.data import bible_data

from models import Scripture, Book


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