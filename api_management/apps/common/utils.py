import datetime
from django.utils import timezone


def same(number):
    return number


def as_local_datetime(a_date):
    return a_date.astimezone(timezone.get_current_timezone())


def date_at_midnight(a_date):
    local_date = as_local_datetime(a_date)
    return datetime.datetime(local_date.year, local_date.month, local_date.day)
