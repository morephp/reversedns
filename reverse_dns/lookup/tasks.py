import subprocess, shlex, re
from datetime import datetime as datetime

import csv, codecs, cStringIO

import datetime as datetime_mod

from django.conf import settings

from celery.task import Task
import pywhois

from reverse_dns.lookup import models
from reverse_dns import mailer

DATE = datetime.strftime(datetime.now(),'%m.%d.%y')

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)(errors='ignore')

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def get_or_create_object(lookupobj, **kwargs):
	try:
		obj = lookupobj.objects.get(**kwargs)
		return obj
	except lookupobj.DoesNotExist:
		obj = lookupobj(**kwargs)
		obj.save()
		return obj

def write_csv(domains, ipobj):
	import csv
	import codecs
	with open('%s/%s.%s.csv' % (settings.WHOIS_OUTPUT_DIR, ipobj.ip_address, DATE), 'w') as csvfile:
		writer = UnicodeWriter(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
		header = ['Domain Name', 'registrar', 'Whois Url', 
				   'Domain Created Date', 'Domain Updated Date', 
				   'Domain Expiration Date', 'Name Servers', 'Domain Contact']
		writer.writerow(header)
		
		for domain in domains:
			row = []
			row.append(domain.domain_name)
			row.append(domain.registrar.replace('|','').replace('\n', ' ').replace(',',' '))
			row.append(domain.whois_server_url)
			row.append(str(domain.domain_created_date))
			row.append(str(domain.domain_updated_date))
			row.append(str(domain.domain_expiration_date))
			
			nameserver = ''
			for server in domain.nameservers():
				nameserver += server.replace('|','') + ' '
			row.append(nameserver)
			
			#stat = ''
			#for status in domain.statuses():
			#	stat += status.replace('|','') + ' '
			#row.append(stat)

			contacts = ''
			for contact in domain.contacts():
				contacts += contact.replace('|','') + ' '
			
			contacts = contacts.replace('None',' ')
			row.append(contacts)
			writer.writerow(row)

		# if len(old_domains) > 0:
		# 	writer.writerow([])
		# 	writer.writerow(['Domains Added on %s' % LAST_UPLOADED_DATE or ''])
		# 	writer.writerow([])

		# for domain in old_domains:
		# 	row = []
		# 	row.append(domain.domain_name)
		# 	row.append(domain.registrar.replace('|','').replace('\n', ' ').replace(',',' '))
		# 	row.append(domain.whois_server_url)
		# 	row.append(str(domain.domain_created_date))
		# 	row.append(str(domain.domain_updated_date))
		# 	row.append(str(domain.domain_expiration_date))
			
		# 	nameserver = ''
		# 	for server in domain.nameservers():
		# 		nameserver += server.replace('|','') + ' '
		# 	row.append(nameserver)
			
		# 	#stat = ''
		# 	#for status in domain.statuses():
		# 	#	stat += status.replace('|','') + ' '
		# 	#row.append(stat)

		# 	contacts = ''
		# 	for contact in domain.contacts():
		# 		contacts += contact.replace('|','') + ' '
			
		# 	contacts = contacts.replace('None',' ')
		# 	row.append(contacts)


			# print row
			# writer.writerow(row)
		return True

def email_admin(user, domains, ipobj):
	if len(domains) > 0:
		if write_csv(domains, ipobj):
			import os
			filepath = os.path.abspath('%s/%s.%s.csv' % (settings.WHOIS_OUTPUT_DIR, ipobj.ip_address, DATE))
			subject = 'New Domains for IP %s' % ipobj.ip_address
			mailer.send_mail_with_attachment(subject=subject, to_email=[user.email,], filepath=filepath)
			uploaded = models.IpUploaded()
			uploaded.ip_address = ipobj
			uploaded.uploaded_date = datetime.now()
			uploaded.save()

def resolve_contact(contact_info, contact_type, domain):
	
	if len(contact_info) == 0: return

	if 'Private' in contact_info[0]: return 

	city_pattern = r'(\w*,?\s)+[0-9]+'
	domain_contact = models.DomainContact()
	domain_contact.domain = domain
	domain_contact.contact_type = contact_type
	

	if len(contact_info) < 6: 
		domain_contact.contact_person = contact_info[0]
		domain_contact.contact_add1 = contact_info[1]
		domain_contact.contact_add1 = contact_info[2]
		if re.match(city_pattern, contact_info[3]):
			try:
				domain_contact.contact_city = contact_info[3]
				domain_contact.contact_country = contact_info[4]
				domain_contact.contact_phone = contact_info[5]

			except:
				pass
	else:
	
		domain_contact.contact_person = contact_info[0]
		domain_contact.contact_org = contact_info[1]
		domain_contact.contact_add1 = contact_info[2]
		if re.match(city_pattern, contact_info[3]):
			try:
				domain_contact.contact_city = contact_info[4]
				domain_contact.contact_country = contact_info[5]
				domain_contact.contact_phone = contact_info[6]
			except:
				pass
		else:
			try:
				domain_contact.contact_add2 = contact_info[4]
				domain_contact.contact_city = contact_info[5]
				domain_contact.contact_country = contact_info[6]
				domain_contact.contact_phone = contact_info[7]
			except:
				pass

	domain_contact.save()


def call_whois(domain, ipobj):

	print domain
	whois = pywhois.whois(domain.domain_name)
	#save whois text to file
	f = open('%s/%s.%s.txt' % (settings.WHOIS_OUTPUT_DIR, domain.domain_name, DATE), 'w')
	f.write(whois.text)
	domain.registrar = '\n'.join(whois.registrar if hasattr(whois, 'registrar') else ' \n ')
	domain.registrar = domain.registrar.split('\n')[0]
	domain.whois_server_url = ' '.join(whois.whois_server if hasattr(whois, 'whois_server') else '')
	
	try:
		domain.domain_created_date = datetime.strptime(whois.creation_date[0],'%d-%b-%Y')
		domain.domain_updated_date = datetime.strptime(whois.updated_date[0],'%d-%b-%Y')
		domain.domain_expiration_date = datetime.strptime(whois.expiration_date[0],'%d-%b-%Y')
	except:
		pass

	for nameserver in whois.name_servers:
		dns_server = models.DomainNameServer(domain=domain, nameserver=nameserver, entity_active=True)
		dns_server.save()

	#for status in whois.status:
	#	domain_status = models.DomainStatus(domain=domain, domain_status=status, entity_active=True)
	#	domain_status.save()

	resolve_contact(whois.admin_contact if hasattr(whois,'admin_contact') else [], 'admin_contact', domain)
	resolve_contact(whois.tech_contact if hasattr(whois,'tech_contact') else [], 'tech_contact', domain)
	

	



def add_domains_task(user, ip_address, domains):
	ipobj = get_or_create_object(models.IPAddress, **dict(ip_address=ip_address, entity_active=True))
	email_domains = []
	for domain in domains.splitlines():
		if len(domain) == 0: continue
		domainobj = get_or_create_object(models.Domain, **dict(domain_name=domain.replace('\n','').strip(), ip_address=ipobj, entity_active=True))
		# domainobj = models.Domain(**dict(ip_address=ipobj, domain_name=domain, entity_active=True))
		domainobj.save()
		if not domainobj.created_date:
			domainobj.created_date = datetime.now()
			domainobj.updated_date = datetime.now()
			domainobj.save()
		# if domainobj:
		# 	email_domains.append(domainobj)
		# 	if not domainobj.created_date:
		# 		domainobj.created_date = datetime.now()
		# 		domainobj.updated_date = datetime.now()
		# 	else:

		# 		domainobj.updated_date = datetime.now()
			try:
				call_whois(domainobj, ipobj)
				email_domains.append(domainobj)
				domainobj.save()
			except Exception, e:
				print 'exception occured'
				print e.message
				pass
	# try:
	# 	# uploaded = ipobj.ipuploaded_set.all().order_by('-uploaded_date')[:1]
	# 	# LAST_UPLOADED_DATE = uploaded[0].__unicode__()
	# 	# print LAST_UPLOADED_DATE
	# 	# old_domains = models.Domain.objects.filter(created_date__range=(uploaded[0].uploaded_date,uploaded[0].uploaded_date+datetime_mod.timedelta(days=1)))
	# except Exception, e:
	# 	print '>>>>>>>>>>>>>>'
	# 	print e.message
	# 	LAST_UPLOADED_DATE = ''
	# 	old_domains = []

	email_admin(user, email_domains, ipobj)

class AddDomainsTask(Task):
	def run(self,user, ip_address, domains, **kwargs):
		add_domains_task(user, ip_address, domains)
