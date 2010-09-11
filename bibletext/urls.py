from django.conf.urls.defaults import *


urlpatterns = patterns('bibletext.views',
    url(r'^(?P<version>\w*)/(?P<book_id>\d*)/(?P<chapter>\d*)/$', 'chapter', name='bibletext_chapter_detail'),
)
