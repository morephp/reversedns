from django.db import models
from django import forms

class IPAddress(models.Model):
	ip_address = models.CharField(max_length=100)
	entity_active = models.BooleanField()

	def __unicode__(self):
		return self.ip_address

	def uploaded(self):
		try:
			return self.ipuploaded_set.get()
		except: 
			return None

class IpUploaded(models.Model):

	ip_address = models.ForeignKey(IPAddress)
	uploaded_date = models.DateField()

	def __unicode__(self):
		from datetime import datetime
		return datetime.strftime(self.uploaded_date,'%d-%b-%Y')

	class Meta:
		ordering = ('-uploaded_date',)



class Domain(models.Model):
	ip_address = models.ForeignKey(IPAddress)
	domain_name = models.CharField(max_length=100)
	entity_active = models.BooleanField()
	registrar = models.CharField(max_length=100)
	whois_server_url = models.CharField(max_length=100)
	domain_created_date = models.DateField(blank=True, null=True)
	domain_updated_date = models.DateField(blank=True, null=True)
	domain_expiration_date = models.DateField(blank=True, null=True)
	created_date = models.DateField(blank=True, null=True)
	updated_date = models.DateField(blank=True, null=True)

	def __unicode__(self):
		return self.domain_name

	def attrs(self):
		keys = ['domain_name', 'registrar', 'whois_server_url', 'domain_created_date', 'domain_updated_date', 'domain_expiration_date']
		return keys

	def nameservers(self):
		return [ns.nameserver for ns in self.domainnameserver_set.all()]

	def statuses(self):
		return [status.domain_status for status in self.domainstatus_set.all()]

	def contacts(self):
		return ['%s %s %s %s %s %s %s' % (
			contact.contact_person + ',' if contact.contact_person else '', 
			contact.contact_org + ',' if contact.contact_org else '', 
			contact.contact_add1 + ',' if contact.contact_add1 else '',
			contact.contact_add2 + ',' if contact.contact_add2 else '',
			contact.contact_city + ',' if contact.contact_city else '',
			contact.contact_country + ',' if contact.contact_country else '',
			contact.contact_phone if contact.contact_phone else '') for contact in self.domaincontact_set.all()]


class DomainNameServer(models.Model):
	domain = models.ForeignKey(Domain)
	nameserver = models.CharField(max_length=100)
	entity_active = models.BooleanField()

	def __unicode__(self):
		return self.nameserver

class DomainStatus(models.Model):
	domain = models.ForeignKey(Domain)
	domain_status = models.CharField(max_length=100)
	entity_active = models.BooleanField()

	def __unicode__(self):
		return self.domain_status

class DomainContact(models.Model):
	domain = models.ForeignKey(Domain)
	contact_type = models.CharField(max_length=100, blank=True, null=True)
	contact_person = models.CharField(max_length=100, blank=True, null=True)
	contact_org = models.CharField(max_length=100, blank=True, null=True)
	contact_add1 = models.CharField(max_length=100, blank=True, null=True)
	contact_add2 = models.CharField(max_length=100, blank=True, null=True)
	contact_city = models.CharField(max_length=100, blank=True, null=True)
	contact_country = models.CharField(max_length=100, blank=True, null=True)
	contact_phone = models.CharField(max_length=100, blank=True, null=True)

	def __unicode__(self):
		return '%s %s' % (self.contact_type, self.contact_person)

