from django import template
from django.utils.safestring import mark_safe

register = template.Library()

from bible import Passage # python-bible module.

from bibletext.models import Book, KJV


@register.inclusion_tag('bibletext/books.html')
def books(bible=KJV):
    """
    Renders all the books from :model:`bibletext.Books`
    
    Uses :template:`bibletext/books.html` to render the books.
    You override this template.
    
    @args
            
        ``bible``: The model object of the translation you want to list books from.
        Defaults to the :model:`bibletext.KJV` text.
    
    Usage::
        
        {% books %}, {% books MyTranslation %}
    
    """
    return {
        'books' : Book.objects.all(),
    }