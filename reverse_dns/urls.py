from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', include('reverse_dns.lookup.urls')),
    url(r'^login/', 'reverse_dns.lookup.views.login', name='login'),
    url(r'^lookup/', include('reverse_dns.lookup.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login_user/$','login_user',name='login_user'),
)
