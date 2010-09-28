from django.conf.urls.defaults import *


urlpatterns = patterns('bibletext.views',
    url(r'^$', 'bible_list', name='bibletext_bible_list'),
    url(r'^(?P<version>\w{2,12})/$', 'bible', name='bibletext_bible_detail'),
    url(r'^(?P<version>\w{2,12})/(?P<book_id>\d+)/$', 'book', name='bibletext_book_detail'),
    url(r'^(?P<version>\w{2,12})/(?P<book_id>\d+)/(?P<chapter_id>\d+)/$', 'chapter', name='bibletext_chapter_detail'),
    url(r'^(?P<version>\w{2,12})/(?P<book_id>\d+)/(?P<chapter_id>\d+)/(?P<verse_id>\d+)/$', 'verse', name='bibletext_verse_detail'),
)
