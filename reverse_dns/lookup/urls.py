from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('reverse_dns.lookup.views',
    
    ## add url for login page
    url(r'^$', 'add_domains',name='add_domains'),
    url(r'^logout', 'logout',name='logout'),
    url(r'^add_domains/$','add_domains',name='add_domains'),
    url(r'^paginate_domains/$','paginate_domains',name='paginate_domains'),
	url(r'^poll_celery_task/$','poll_celery_task',name='poll_celery_task'),
	
)
