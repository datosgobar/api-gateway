# flake8: noqa
# pylint: disable=ungrouped-imports
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six


try:
    from http.client import OK, CREATED, CONFLICT, NO_CONTENT, \
        NOT_FOUND, BAD_REQUEST, INTERNAL_SERVER_ERROR, HTTPConnection
except ImportError:  # pragma: no cover
    from httplib import OK, CREATED, CONFLICT, NO_CONTENT, \
        NOT_FOUND, BAD_REQUEST, INTERNAL_SERVER_ERROR, HTTPConnection

try:
    # noqa: F401
    from urllib.parse import urlparse, urljoin, urlencode, quote,\
        unquote, parse_qs, parse_qsl, ParseResult
except ImportError:  # pragma: no cover
    from urlparse import urlparse, urljoin, parse_qs, parse_qsl, ParseResult
    from urllib import urlencode, quote, unquote

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

try:
    from unittest import TestCase, skipIf, main as run_unittests
except ImportError:  # pragma: no cover
    from unittest2 import TestCase, skipIf, main as run_unittests


def utf8_or_str(text):
    if six.PY2:
        return text.encode('utf-8')
    return text
