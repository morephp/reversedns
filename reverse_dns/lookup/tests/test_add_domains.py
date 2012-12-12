"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from reverse_dns.lookup.tasks import add_domains_task
from reverse_dns.lookup import models


class AddDomainsTest(TestCase):


	def test_add_domains_task(self):
		ip_address = '192.168.0.1'
		f = open('/tmp/domains.txt')
		add_domains_task(ip_address, f)
		self.assertTrue(True)
		domain = models.Domain.objects.all()
		for d in domain:
			print d 
			print d.registrar
			print [c for c in d.domaincontact_set.all()]
			print [c for c in d.domainnameserver_set.all()]
			print [c for c in d.domainstatus_set.all()]