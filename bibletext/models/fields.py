from django import forms
from django.core import exceptions
from django.db import models

from bible import Verse, RangeError # python-bible module.


class VerseFormField(forms.CharField):
    def clean(self, value):
        """Form field for custom validation entering verses"""
        if not value:
            return super(VerseFormField, self).clean(value)
        
        try:
            verse = Verse(value)
        except (RangeError, Exception) as err:
            raise forms.ValidationError(err.__str__())
        
        # Return the cleaned and processed data. NB: We use the formatted string for ease of reading/editing.
        return super(VerseFormField, self).clean(verse.format())


class VerseField(models.CharField):
    description = "A scripture reference to a specific verse"
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('max_length'):
            kwargs['max_length'] = 100
        super(VerseField, self).__init__(*args, **kwargs)
    
    def db_type(self):
        return 'char(%s)' % self.max_length
    
    def formfield(self, **kwargs):
        defaults = {'form_class': VerseFormField}
        defaults.update(kwargs)
        return super(VerseField, self).formfield(**defaults)