from django.contrib import admin

from .models import KongApi, TokenRequest, KongPluginHttpLog,\
    KongPluginRateLimiting, KongPluginJwt, \
    KongConsumer, JwtCredential


class KongObjectInline(admin.StackedInline):
    readonly_fields = ('kong_id', )


class KongPluginHttpLogInline(KongObjectInline):
    model = KongPluginHttpLog


class KongPluginRateLimitingInline(KongObjectInline):
    model = KongPluginRateLimiting


class KongPluginJwtInline(KongObjectInline):
    model = KongPluginJwt


@admin.register(KongApi)
class ApiAdmin(admin.ModelAdmin):
    inlines = [
        KongPluginHttpLogInline,
        KongPluginRateLimitingInline,
        KongPluginJwtInline,
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


class JwtCredentialInline(KongObjectInline):
    model = JwtCredential

    readonly_fields = KongObjectInline.readonly_fields + ('key', 'secret', )

    fieldsets = (
        (None, {
            'fields': ('kong_id', )
        }),
        ('Keys', {
            'classes': ('collapse',),
            'fields': ('key', 'secret', ),
        }),
    )


@admin.register(KongConsumer)
class KongConsumerAdmin(admin.ModelAdmin):

    list_display = ['api', 'applicant', 'contact_email', 'kong_id']

    exclude = ('enabled', )

    readonly_fields = ('kong_id', )

    inlines = (JwtCredentialInline, )
