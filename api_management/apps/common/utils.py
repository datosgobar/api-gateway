import datetime

from dateutil import relativedelta
from django.utils import timezone


def same(number):
    return number


def date_at_midnight(a_date):
    return datetime.datetime(a_date.year, a_date.month, a_date.day)


def last_n_days(days):
    return timezone.now() - relativedelta.relativedelta(days=days)
