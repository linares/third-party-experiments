from django.conf.urls.defaults import patterns, include, url
from apps.landing import urls

urlpatterns = patterns('',
    url(r'^$', 'marissa.apps.landing.views.home', name='home'),
    url(r'^twitter_signed_in$', 'marissa.apps.thirdparty.views.twitter_signed_in', name='home'),
    url(r'^landing$', 'marissa.apps.landing.views.signin', name='home'),
    url(r'^landing', include(urls)),
    url(r'^oauth$', 'marissa.apps.thirdparty.views.oauth_req')
)
