from re import error

from bible import data, book_re # python-bible module.

from models import Book, KJV


# Exceptions
class BibleError(Exception):
    pass

def BookError(BibleError):
    pass


def find_book(book, bible=KJV):
    " Find the book reference and return the :model:`bibletext.Book` "
    try:
        # Does the text look like a book reference?
        b = book_re.search(book).group(0)
    except error:
        raise BookError("Could not find that book of the Bible: %s." % book)
        
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
    try:
        return Book.objects.get(pk=found)
    except Book.ObjectDoesNotExist:
        raise BookError("Could not find that book of the Bible: %d." % book)