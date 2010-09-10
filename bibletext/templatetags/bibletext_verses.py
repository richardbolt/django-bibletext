from django import template
from django.utils.safestring import mark_safe

register = template.Library()

from bible import Passage
from bibletext.models import KJV


@register.inclusion_tag('bibletext/verse.html')
def verse(reference, bible=KJV):
    """
    Renders a verse from :model:`bibletext.KJV` (or another ``bible``)
    
    Uses :template:`bibletext/verse.html` to render the verse.
    You override this template.
    
    @args
        
        ``reference``: The textual scripture reference. eg: 'Jn 3:16'
    
        ``bible``: The model object of the translation you want to quote from.
        Defaults to the :model:`bibletext.KJV` text.
    
    Usage::
        
        {% verse 'John 3:16' %}, {% verse 'John 3:16', MyTranslation %}
    """
    verse = bible.objects.verse(reference)
    
    return {
        'verse' : verse,
        'bible': bible,
    }

@register.inclusion_tag('bibletext/passage.html')
def passage(start_reference, end_reference, bible=KJV):
    """
    Renders a passage from :model:`bibletext.KJV` (or another ``bible``)
    
    Uses :template:`bibletext/passage.html` to render the passage.
    You override this template.
    
    @args
        
        ``start_reference``: The textual scripture reference to start from. eg: 'Jn 3:16'
        
        ``end_reference``: The textual scripture reference to end with. eg: 'Jn 3:18'
        
        ``bible``: The model object of the translation you want to quote from.
        Defaults to the :model:`bibletext.KJV` text.
    
    Usage::
        
        {% passage 'John 3:16' 'John 3:18' %}, {% passage 'John 3:16' 'John 3:18' MyTranslation %}
    """
    verse_list = bible.objects.passage(start_reference, end_reference)
    passage = Passage(start_reference, end_reference) # Call {{ passage.format }} for the scripture reference.
    
    return {
        'verse_list' : verse_list,
        'passage': passage,
        'bible': bible,
    }