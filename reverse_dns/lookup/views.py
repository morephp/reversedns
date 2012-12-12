from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.contrib.auth import authenticate, login as dns_login, logout as dns_logout
from django.contrib.auth.decorators import login_required

from celery.result import AsyncResult

from reverse_dns.lookup.tasks import AddDomainsTask
from reverse_dns.lookup import models


def login(request,template='login.html'):
	error = None
	if request.method == 'POST':
		username = request.POST.get('username',None)
		password = request.POST.get('password',None)
		if not username or not password:
			error = 'Please enter both a username and password'
		else:
			user = authenticate(username=username, password=password)
			if not user:
				error = 'Invalid Login'
			else:
				dns_login(request, user)
				return HttpResponseRedirect('/lookup/add_domains')
	
	return render_to_response(template,
                              dict(title='Welcome to Revese DN Lookup!', error=error),
                              context_instance=RequestContext(request))  

@login_required
def add_domains(request, template='index.html'):
	if request.method == 'POST':
		ip_address = request.POST.get('ip_address')
		domains_file = request.FILES.get('domains')
		domains = domains_file.read()
		task = AddDomainsTask.delay(request.user, ip_address, domains)
		request.session['task_id'] = task.id
		return render_to_response('polling.html',
                              dict(title='Welcome to Reverse DNS Lookup!!', message='Please wait for processing'),
                              context_instance=RequestContext(request)) 
	else:
		
		return render_to_response(template, dict(
                              			title='Welcome to Reverse DNS Lookup!!',),
                              		 	context_instance=RequestContext(request)
                              		 ) 

def poll_celery_task(request):
	task_id = request.session.get('task_id',None)
	if task_id:
		result = AsyncResult(task_id)
		if result.ready():
			return HttpResponse(simplejson.dumps([dict(status = 200)]), content_type = 'application/javascript; charset=utf8')
		else:
			return HttpResponse(simplejson.dumps([dict(status = 100)]), content_type = 'application/javascript; charset=utf8')
	return HttpResponse(simplejson.dumps([dict(status = 500)]), content_type = 'application/javascript; charset=utf8')

def logout(request):
	dns_logout(request)
	return HttpResponseRedirect('/')

def paginate_domains(request):
	
	if request.method == 'POST':

		result = dict()

		dispaly_start = request.POST.get('iDisplayStart')
		display_length = request.POST.get('iDisplayLength')

		ips = models.IPAddress.objects.all().order_by('-ipuploaded__uploaded_date')[dispaly_start : (int(dispaly_start) + int(display_length))]

		aaData = []
		for ip in ips:
			if len(ip.ipuploaded_set.all()) > 0:
				for date in ip.ipuploaded_set.all():
					sublist = []
					sublist.append(ip.ip_address)
					sublist.append(date.__unicode__())

					aaData.append(sublist)
			else:
				sublist = []
				sublist.append(ip.ip_address)
				sublist.append('')
				aaData.append(sublist)

		result['aaData'] = aaData
		result['sEcho'] = request.POST.get('sEcho')
		result['iTotalRecords'] = len(models.IPAddress.objects.all())
		result['iTotalDisplayRecords'] = len(models.IPAddress.objects.all())


		return HttpResponse(simplejson.dumps(result), content_type = 'application/javascript; charset=utf8')