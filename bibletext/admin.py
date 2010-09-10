from django import forms
from django.contrib import admin
from django.contrib.contenttypes import generic

from bible import Verse, RangeError # python-bible

from models import Scripture


class ScriptureForm(forms.ModelForm):
    class Meta:
        model = Scripture

    def clean(self):
        # Checking to see if the start (and end) verse is in the given
        # version, if not populate the appropriate self._errors entry.
        version = self.cleaned_data['version'].model_class().translation
        if 'start_verse' in self.cleaned_data:
            try:
                verse = Verse(self.cleaned_data['start_verse']+' '+version)
            except (RangeError, Exception) as err:
                self._errors['start_verse'] = self.error_class([err.__str__()])
                del self.cleaned_data['start_verse']
        if 'end_verse' in self.cleaned_data and self.cleaned_data['end_verse']:
            try:
                verse = Verse(self.cleaned_data['end_verse']+' '+version)
            except (RangeError, Exception) as err:
                self._errors['end_verse'] = self.error_class([err.__str__()])
                del self.cleaned_data['end_verse']
        
        return super(ScriptureForm, self).clean()


class ScriptureInline(generic.GenericTabularInline):
    "Import and use wherever you wish for inline scripture adding/editing."
    model = Scripture
    form = ScriptureForm
    fields = ('start_verse', 'end_verse', 'version')
    extra = 1


class ScriptureAdmin(admin.ModelAdmin):
    list_display = ('start_verse', 'end_verse', 'version', 'start_book', 'end_book')
    list_filter = ('version', 'start_book')
    fields = ('start_verse', 'end_verse', 'version')
    form = ScriptureForm

admin.site.register(Scripture, ScriptureAdmin)