# pylint: skip-file
from django.core.paginator import Paginator
from django.db import connection


class LargeTablePaginator(Paginator):
    """
    Source: https://medium.com/squad-engineering/
    estimated-counts-for-faster-django-admin-change-list-963cbf43683e
    Warning: Postgresql only hack
    Overrides the count method of QuerySet objects to get an estimate instead
    of actual count when not filtered. However, this estimate can be stale and
    hence not fit for situations where the count of objects actually matter.
    """
    def _get_count(self):
        if getattr(self, '_count', None) is not None:
            return self._count
        query = self.object_list.query
        if not query.where:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT reltuples FROM pg_class WHERE relname = %s",
                               [query.model._meta.db_table])
                self._count = int(cursor.fetchone()[0])
            except Exception as _:
                self._count = super(LargeTablePaginator, self)._get_count()
        else:
            self._count = super(LargeTablePaginator, self)._get_count()
        return self._count
    count = property(_get_count)
