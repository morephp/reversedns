from django.template.loader import get_template
from django.template import Context
from django.core import mail


def send_email(domains, ipobj, subject=None, template_name='email_template.html', fail_silently=True):

	t = get_template(template_name)
	c = Context(dict(domains = domains))

	
	params = dict(
		subject = subject or 'New domains for IP: %s' % ipobj.ip_address,
		body = t.render(c),
		from_email = 'admin@webiken.net',
		to = settings.SITE_ADMIN_EMAILS,
		)
		
	try:
		connection = mail.get_connection(fail_silently=fail_silently)
		connection.open()
		email = mail.EmailMessage(**params)
		email.content_subtype = "html"
		email.send()
		connection.close()
	except ValueError, e:
		raise ValueError('Invalid backend argument')

def send_mail_with_attachment(subject=None,to_email=None, filepath=None, fail_silently=False):

	params = dict(
		subject = subject,
		body = 'CSV File Attached',
		from_email = 'admin@webiken.net',
		to = to_email,
		)
		
	try:
		connection = mail.get_connection(fail_silently=fail_silently)
		connection.open()
		email = mail.EmailMessage(**params)
		email.attach_file(filepath)
		email.send()
		connection.close()
	except ValueError, e:
		raise ValueError('Invalid backend argument')