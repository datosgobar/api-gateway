from django.contrib import admin

from rest_framework.authtoken.admin import TokenAdmin

from .models import Query

admin.site.register(Query)

TokenAdmin.raw_id_fields = ('user',)
