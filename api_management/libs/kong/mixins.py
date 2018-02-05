# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from abc import ABCMeta

from six import with_metaclass

from .utils import parse_query_parameters


class CollectionMixin(with_metaclass(ABCMeta, object)):  # pylint: disable=too-few-public-methods

    def iterate(self, window_size=10, **filter_fields):
        current_offset = None
        while True:
            response = self.list(size=window_size, offset=current_offset, **filter_fields)
            for item in response['data']:
                yield item
            next_url = response.get('next', None)
            if next_url is None:
                return
            current_offset = parse_query_parameters(next_url).get('offset')[0]
