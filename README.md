Django App for a full fledged bible viewer
------------------------------------------
A Django app that has a full bible viewer, including the KJV text by default.
Other translation texts can be easily added. Also includes scripture models
and admin definitions to easily add your own scripture verse and passages
to your project.

Uses [python-bible](http://github.com/jasford/python-bible) for
computing and handling the verse and passage lookups. You will need that
on your path somewhere - note that you'll need to use this fork currently
until the original python-bible implementation is fixed: [python-bible](http://github.com/richardbolt/python-bible)

Including the translation in a Verse object is optional, but if used, the
omitted verses will be accounted for when interacting with the Verse or
Passage that it is in. Passages can not combine two Verse objects that are
not from the same translation. While any translation can be entered and
stored in the objects, the only ones with special data are: KJV, ESV, RSV,
NIV, NASB, NRSV, NCV, and LB.
