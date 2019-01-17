from django.db.backends.postgresql_psycopg2.base import *  # noqa: F403
import pytz


def local_tzinfo_factory(offset):
    """
    Create a tzinfo object using the offset of the db connection. This ensures
    that the datetimes returned are timezone aware and will be printed in the
    reports with timezone information.
    """
    return pytz.FixedOffset(offset)


class DynamicTimezoneDatabaseWrapper(DatabaseWrapper):  # noqa: F405
    """
    This exists to allow report generation SQL to set the time zone of the
    connection without interference from Django, which normally tries to
    ensure that all connections are UTC if `USE_TZ` is `True`.
    """

    def create_cursor(self):
        cursor = self.connection.cursor()
        cursor.tzinfo_factory = local_tzinfo_factory
        return cursor


DatabaseWrapper = DynamicTimezoneDatabaseWrapper
