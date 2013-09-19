from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', lambda r : HttpResponseRedirect('training/')),
    url(r'^training/', include('training.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
