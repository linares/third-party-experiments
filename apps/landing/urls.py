from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
import os

urlpatterns = patterns('',    
    url(r'pages/(?P<page_id>[^/]+).html', 'marissa.apps.landing.views.page', name='page'),
    
)
