from django.db.backends.postgresql_psycopg2.base import *  # noqa


class DynamicTimezoneDatabaseWrapper(DatabaseWrapper):
    '''
    This exists to allow report generation SQL to set the time zone of the
    connection without interference from Django, which normally tries to
    ensure that all connections are UTC if `USE_TZ` is `True`.
    '''

    def create_cursor(self):
        cursor = self.connection.cursor()
        cursor.tzinfo_factory = None
        return cursor


DatabaseWrapper = DynamicTimezoneDatabaseWrapper
