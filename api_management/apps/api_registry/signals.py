import django.dispatch

token_request_accepted = django.dispatch.Signal(providing_args=[])
