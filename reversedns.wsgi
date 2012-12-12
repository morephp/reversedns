import os
import sys
import site

#sys.path.append('/home/admin/.virtualenvs/reversedns/lib/python2.7/site-packages/')

site.addsitedir('/home/admin/.virtualenvs/reversedns/lib/python2.7/site-packages/')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reverse_dns.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
