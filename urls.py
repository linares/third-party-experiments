from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'marissa.apps.landing.views.home', name='home'),
    url(r'^twitter_signed_in$', 'marissa.apps.thirdparty.views.twitter_signed_in', name='home'),
    url(r'^landing$', 'marissa.apps.landing.views.signin', name='home'),
    url(r'^oauth$', 'marissa.apps.thirdparty.views.oauth_req')
)
