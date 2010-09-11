from django.conf.urls.defaults import *


urlpatterns = patterns('bibletext.views',
    url(r'^(?P<version>\w{2,12})/(?P<book_id>\d+)/(?P<chapter>\d+)/$', 'chapter', name='bibletext_chapter_detail'),
    url(r'^(?P<version>\w{2,12})/(?P<book_id>\d+)/(?P<chapter>\d+)/(?P<verse>\d+)/$', 'verse', name='bibletext_verse_detail'),
)
