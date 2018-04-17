import django.dispatch

# pylint: disable=invalid-name
token_request_accepted = django.dispatch.Signal(providing_args=['instance'])
