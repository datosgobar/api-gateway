import datetime
from django.utils import timezone


def same(number):
    return number


def as_locale_datetime(a_date):
    return a_date.astimezone(timezone.get_current_timezone())


def date_at_midnight(a_date):
    locale_date = as_locale_datetime(a_date)
    return datetime.datetime(locale_date.year, locale_date.month, locale_date.day)
