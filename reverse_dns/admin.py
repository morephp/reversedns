from django.contrib import admin

from reverse_dns.lookup import models

admin.site.register(models.IPAddress)
admin.site.register(models.Domain)
