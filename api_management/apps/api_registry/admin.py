from django.contrib import admin

from .models import ApiData


@admin.register(ApiData)
class ApiAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name', 'documentation_url', 'upstream_url', 'uris', 'enabled')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('hosts', 'strip_uri', 'preserve_host', 'kong_id',),
        }),
        ('Rate Limiting', {
            'classes': ('collapse',),
            'fields': ('rate_limiting_enabled',
                       'rate_limiting_second',
                       'rate_limiting_minute',
                       'rate_limiting_hour',
                       'rate_limiting_day')
        })
    )

    def add_view(self, request, form_url='', extra_context=None):
        self.readonly_fields = ('kong_id',)
        return super(ApiAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.readonly_fields = ('name', 'kong_id')

        if ApiData.objects.get(pk=object_id).rate_limiting_enabled:
            self.readonly_fields += ('rate_limiting_second',
                                     'rate_limiting_minute',
                                     'rate_limiting_hour',
                                     'rate_limiting_day')
        return super(ApiAdmin, self).change_view(request, object_id, form_url, extra_context)
