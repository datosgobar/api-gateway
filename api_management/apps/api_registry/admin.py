from django.contrib import admin

from .models import Api


@admin.register(Api)
class ApiAdmin(admin.ModelAdmin):
    fieldsets = ('name', 'upstream_url', 'uri', 'enabled', 'kong_id')
    fieldsets = (
        (None, {
            'fields': ('name', 'upstream_url', 'uri', 'enabled')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('kong_id',),
        }),
    )

    def add_view(self, request, form_url='', extra_context=None):
        self.readonly_fields = ('kong_id',)
        return super(ApiAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.readonly_fields = ('name', 'kong_id')
        return super(ApiAdmin, self).change_view(request, object_id, form_url, extra_context)
