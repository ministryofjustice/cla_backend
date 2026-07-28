import os
from django.db import connection, DatabaseError


def database_healthcheck():
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        return bool(row and row[0] == 1)
    except DatabaseError:
        return False
    finally:
        if cursor is not None:
            cursor.close()


def check_disk():
    stat = os.statvfs(os.getcwd())
    available_mb = (stat.f_bavail * stat.f_frsize) / (1024.0**2)
    total_mb = (stat.f_blocks * stat.f_frsize) / (1024.0**2)

    available_percent = available_mb / total_mb * 100
    status = available_percent > 2.0

    return status
