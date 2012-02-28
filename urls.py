from django.conf.urls.defaults import *

urlpatterns = patterns('wreb.views',
    url(r'ajax/$', 'ajax', name='wreb-ajax'),
    url(r'$', 'build_regex'),
)
