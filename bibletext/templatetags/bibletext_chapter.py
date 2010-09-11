from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe, SafeUnicode

from bibletext.models import KJV
from bibletext.utils import BookError, find_book


register = template.Library()

@register.inclusion_tag('bibletext/chapter.html')
def chapter(book, chapter=1, bible=KJV):
    """
    Renders the chapter from the given :model:`bibletext.Book`
    in the given Bible.
    
    Uses :template:`bibletext/chapter.html` to render the chapter.
    You override this template.
    
    @args
        
        ``book``: The :model:`bibletext.Book` to render the chapter from.
        Note: You can also use an integer book number, or a book name in which case
        the book will be found from bible.books.
        
        ``chapter``: The integer chapter you wish to render.
        
        ``bible``: The model object of the translation you want to render text from.
        Defaults to the :model:`bibletext.KJV` text.
    
    Usage::
        
        {% chapter MyBook 3 %}, {% chapter 1, 1, MyTranslation %}, {% chapter 'Genesis', 1, MyTranslation %}
    
    """
    if type(book) is int:
        if book > 0 and book <= 66:
            # 66 Books in the Bible.
            book = bible.books.objects.get(pk=book)
        else:
            
            # We can't find the given book in the Bible.
            return {
                'bible': None,
                'book': None,
                'chapter': None,
                'verse_list' : bible.objects.none()
            }
            
    elif type(book) in (SafeUnicode, str, unicode):
        # find the book reference
        try:
            book = find_book(book, bible)
        except BookError:
            
            # We can't find the given book in the Bible.
            return {
                'bible': None,
                'book': None,
                'chapter': None,
                'verse_list' : bible.objects.none()
            }
    
    try:
        verse_list = bible.objects.filter(book=book, chapter=int(chapter))
    except bible.DoesNotExist:
        verse_list = bible.objects.none()
    
    return {
        'bible': bible,
        'book': book,
        'chapter': chapter,
        'verse_list' : bible.objects.filter(book=book, chapter=chapter)
    }