from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.utils import timezone
from rest_framework.authtoken.admin import TokenAdmin
from solo.admin import SingletonModelAdmin

from .models import Query, CsvAnalyticsGeneratorTask, GoogleAnalyticsSettings


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/query_change_list.html'

    # Impide hacer un COUNT(*) adicional en el armado de respuesta
    show_full_result_count = False

    list_filter = ['status_code', 'api_data', 'start_time', 'x_source', ]
    search_fields = ['ip_address', 'uri', 'querystring', ]
    list_display = [
        'host', 'uri', 'api_data', 'ip_address',
        'querystring', 'status_code', 'start_time', 'x_source'
    ]

    def get_queryset(self, request):
        today = timezone.now().date()
        week_ago = today - relativedelta(days=7)
        queryset = super(QueryAdmin, self).get_queryset(request)
        return queryset.filter(start_time__gt=week_ago)


TokenAdmin.raw_id_fields = ('user',)


@admin.register(CsvAnalyticsGeneratorTask)
class CsvAnalyticsGeneratorTaskAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'logs'
    ]


@admin.register(GoogleAnalyticsSettings)
class GoogleAnalyticsSettingsAdmin(SingletonModelAdmin):
    list_display = ['ga_id']
