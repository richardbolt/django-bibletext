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
