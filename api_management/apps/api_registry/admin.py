from django.contrib import admin

from .models import ApiData, TokenRequest


@admin.register(ApiData)
class ApiAdmin(admin.ModelAdmin):
    list_display = [
        "name", "enabled", "upstream_url", "hosts", "uris",
    ]

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
        }),
        ('Logs', {
            'classes': ('collapse',),
            'fields': ('httplog2_enabled',
                       'httplog2_api_key',
                       'httplog2_ga_exclude_regex')
        }),
        (None, {
            'fields': ('jwt_enabled',)}),
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
        'state',
    ]
    fields = ('api', 'applicant', 'contact_email', 'consumer_application', 'requests_per_day',
              'state',)

    readonly_fields = ('state', )

    change_form_template = 'token_request_changeform.html'

    def response_change(self, request, obj):

        if "_accept" in request.POST:
            obj.accept()
            self.message_user(request, "Solicitud Aceptada")

        if "_reject" in request.POST:
            obj.reject()
            self.message_user(request, "Solicitud Rechazada")

        return super(TokenRequestAdmin, self).response_change(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if object_id is not None:
            extra_context = extra_context or {}
        extra_context['is_pending'] = TokenRequest.objects.get(id=object_id).is_pending()

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )