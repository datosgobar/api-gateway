from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin

from .models import Query


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = [
        'host', 'uri', 'api_data', 'ip_address',
        'querystring', 'status_code', 'start_time',
    ]
    list_filter = ['status_code', 'api_data', 'start_time', ]
    search_fields = ['ip_address', 'uri', 'querystring', ]


TokenAdmin.raw_id_fields = ('user',)
