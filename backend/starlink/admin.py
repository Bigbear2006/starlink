from django.contrib import admin
from django.contrib.auth.models import Group

from starlink import models

admin.site.register(models.Client)
admin.site.register(models.SupportSection)
admin.site.register(models.FAQ)
admin.site.register(models.Publication)
admin.site.register(models.Plate)
admin.site.unregister(Group)


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_select_related = ['client']
