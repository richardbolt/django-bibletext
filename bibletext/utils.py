from re import error

from django.contrib.contenttypes.models import ContentType

from bible import data, book_re # python-bible module.

from models import VerseText, KJV


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
        return bible.books.objects.get(pk=found)
    except bible.books.ObjectDoesNotExist:
        raise BookError("Could not find that book of the Bible: %d." % book)


def lookup_translation(version):
    " Returns the VerseText implementation based on the translation string ('KJV', 'ASV', etc) "
    bible_content_types = ContentType.objects.filter(pk__in=VerseText.versions)
    for bible_content_type in bible_content_types:
        if bible_content_type.model_class().translation == version:
            return bible_content_type.model_class()
    return KJV # Default to the KJV text to keep it simple.
