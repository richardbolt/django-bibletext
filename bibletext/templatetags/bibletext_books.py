from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe, SafeUnicode

register = template.Library()

from bible import Passage, data, book_re # python-bible module.

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

@register.inclusion_tag('bibletext/chapters.html')
def chapters(book, bible=KJV):
    """
    Renders all the chpaters from the given :model:`bibletext.Book`
    in the given Bible.
    
    Uses :template:`bibletext/chapters.html` to render the chapter numbers.
    You override this template.
    
    @args
        
        ``book``: The :model:`bibletext.Book` to list chapters from.
        Note: You can also use an integer book number, or a book name.
        
        ``bible``: The model object of the translation you want to list chapters from.
        Defaults to the :model:`bibletext.KJV` text.
    
    Usage::
        
        {% chapters MyBook %}, {% chapters 1, MyTranslation %}, {% chapters "Genesis", MyTranslation %}
    
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
            # Does the text look like a book reference?
            b = book_re.search(book).group(0)        
            # Try to find the book listed as a book name or abbreviation
            bible_data = data.bible_data(bible.translation)
            b = b.rstrip('.').lower().strip()
            for i, book_data in enumerate(bible_data):
                if book_data['name'].lower() == b:
                    found = i + 1
                    break
                else:
                    for abbr in book_data['abbrs']:
                        if abbr == b:
                            found = i + 1
                            break
            book = Book.objects.get(pk=found)
        except:
            
            # We can't find the given book in the Bible.
            return {
                'book': None,
                'chapters' : None
            }
    
    return {
        'book': book,
        'chapters' : bible.objects.filter(book=book).values('chapter').annotate(Count('verse'))
    }