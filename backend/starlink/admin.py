from django.contrib import admin

from starlink import models

admin.site.register(models.Client)
admin.site.register(models.Payment)
admin.site.register(models.SupportSection)
admin.site.register(models.Publication)
