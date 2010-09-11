Django App for a full fledged Bible viewer
==========================================

A Django app that has a full Bible viewer, including the KJV text by default.
Other translation texts can be easily added. Also includes scripture models
and admin definitions to easily add your own scripture verse and passages
to your project.

Included out of the box is the King James Version text as the default version.

This project is in it's early stages...

Dependencies
------------

Uses [python-bible](http://github.com/jasford/python-bible) for
computing and handling the verse and passage lookups. You will need that
on your path somewhere - note that you'll need to use this fork currently
until the original python-bible implementation is fixed: [python-bible](http://github.com/richardbolt/python-bible)

Installation
------------

* Make sure the dependencies are satisfied and this module is somewhere on your python path.
* Add `'bibletext'` to your `INSTALLED_APPS` in your `settings.py`.
* Create your database tables: `python manage.py syncdb`.
* Install initial data from fixtures: `python manage.py loaddata books.json kjv.json`.

Usage
-----

### Template tags ###

There are template tags to use:

    {% load bibletext_books bibletest_verses bibletext_chapter %}
    
    All the books of the bible, listed:
    {% books %} or {% books MyTranslation %}
    
    All the chapters and verse counts from John listed:
    {% chapters 'John' %}
    
    The text of John 3 (the whole chapter):
    {% chapter 'John' 3 %}
    
    The text of 3 John (the whole book since chapter defaults to 1, and there is only one chapter):
    {% chapter '3 John' %}
    
    A passage (John 3:16 - 3:18):
    {% passage 'John 3:16 - 3:18' %} or {% passage 'Jn 3:16 - 3:18' %}
    
    A specific verse (John 3:16):
    {% verse 'John 3:16' %} or {% verse 'Jn 3:16' %}
    

### Views and urls ###

The easiest way to include the whole Bible in your website is to add `(r'^bible/', include('bibletext.urls')),` to your **urls.py**.

You may wish to override **templates/bibletext/base.html** and provide some CSS to make it look nice.

Note: Currently only the whole chapter view and a verse view are included,
eg: `KJV/43/3/` gives you John 3 from the KJV,
`KJV/43/3/16/` gives you John 3:16 from the KJV.

More default views and urls forthcoming. Default CSS and standalone templates will also be forthcoming.


### Scripture ###

There is a Scripture model (living in **models/scripture.py**) for usage in your own models like so:
    
**models.py:**
    
    from bibletext.models import Scripture
    
    class Sermon(models.Model):
        title = models.CharField(max_length=100, blank=True)
        date = models.DateField(help_text="Date of the Sermon.")
        preacher = models.ForeignKey(Preacher, blank=True, null=True)
        audio = models.FileField(upload_to='%Y/%m %B')
        published = models.BooleanField(default=True)
    
        scripture = generic.GenericRelation(Scripture) # optional, but provides additional APIs.

**admin.py:**
    
    from bibletext.admin import ScriptureInline

    class SermonAdmin(admin.ModelAdmin):
        inlines = [
            ScriptureInline,
        ]
