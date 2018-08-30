from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin
from .admin_paginator import LargeTablePaginator
from .models import Query


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    # Impide hacer un COUNT(*) adicional en el armado de respuesta
    show_full_result_count = False

    paginator = LargeTablePaginator

    list_display = [
        'host', 'uri', 'api_data', 'ip_address',
        'querystring', 'status_code', 'start_time', 'x_source'
    ]


TokenAdmin.raw_id_fields = ('user',)
