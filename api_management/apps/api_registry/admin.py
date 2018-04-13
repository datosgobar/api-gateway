from django.contrib import admin

from .models import ApiData, TokenRequest, HttpLogData, RateLimitingData, JwtData


class PluginDataInline(admin.StackedInline):
    readonly_fields = ('kong_id', )


class HttpLogDataInline(PluginDataInline):
    model = HttpLogData


class RateLimitingDataInline(PluginDataInline):
    model = RateLimitingData


class JwtDataInline(PluginDataInline):
    model = JwtData


@admin.register(ApiData)
class ApiAdmin(admin.ModelAdmin):
    inlines = [
        HttpLogDataInline,
        RateLimitingDataInline,
        JwtDataInline,
    ]

    list_display = [
        "name", "enabled", "upstream_url", "hosts", "uri",
    ]

    fieldsets = (
        (None, {
            'fields': ('name', 'documentation_url', 'upstream_url', 'uri', 'enabled')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('hosts', 'strip_uri', 'preserve_host', 'kong_id',),
        }),
    )

    def add_view(self, request, form_url='', extra_context=None):
        self.readonly_fields = ('kong_id',)
        return super(ApiAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.readonly_fields = ('name', 'kong_id')
        return super(ApiAdmin, self).change_view(request, object_id, form_url, extra_context)


@admin.register(TokenRequest)
class TokenRequestAdmin(admin.ModelAdmin):
    list_display = [
        'api', 'applicant', 'contact_email', 'consumer_application', 'requests_per_day',
    ]
    fields = ('api', 'applicant', 'contact_email', 'consumer_application', 'requests_per_day', )
