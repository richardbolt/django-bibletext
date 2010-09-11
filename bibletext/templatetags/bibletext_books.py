from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe, SafeUnicode

from bibletext.models import Book, KJV
from bibletext.utils import BookError, find_book


register = template.Library()

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

@register.inclusion_tag('bibletext/chapters.html')
def chapters(book, bible=KJV):
    """
    Renders all the chapters from the given :model:`bibletext.Book`
    in the given Bible.
    
    Uses :template:`bibletext/chapters.html` to render the chapter numbers.
    You override this template.
    
    @args
        
        ``book``: The :model:`bibletext.Book` to list chapters from.
        Note: You can also use an integer book number, or a book name.
        
        ``bible``: The model object of the translation you want to list chapters from.
        Defaults to the :model:`bibletext.KJV` text.
    
    Usage::
        
        {% chapters MyBook %}, {% chapters 1, MyTranslation %}, {% chapters 'Genesis', MyTranslation %}
    
    """
    if type(book) is int:
        if book > 0 and book <= 66:
            # 66 Books in the Bible.
            book = Book.objects.get(pk=book)
        else:
            
            # We can't find the given book in the Bible.
            return {
                'book': None,
                'chapters' : None
            }
            
    elif type(book) in (SafeUnicode, str, unicode):
        # find the book reference
        try:
            book = find_book(book, bible)
        except BookError:
            
            # We can't find the given book in the Bible.
            return {
                'book': None,
                'chapters' : None
            }
    
    return {
        'book': book,
        'chapters' : bible.objects.filter(book=book).values('chapter').annotate(Count('verse'))
    }