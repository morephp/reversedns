from django.contrib import admin

from reverse_dns.lookup import models

admin.site.register(models.IPAddress)
admin.site.register(models.Domain)
admin.site.register(models.DomainStatus)
admin.site.register(models.DomainNameServer)
admin.site.register(models.DomainContact)
admin.site.register(models.IpUploaded)
