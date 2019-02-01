import os


def check_disk():
    stat = os.statvfs(os.getcwd())
    available_mb = (stat.f_bavail * stat.f_frsize) / (1024.0 ** 2)
    total_mb = (stat.f_blocks * stat.f_frsize) / (1024.0 ** 2)

    available_percent = available_mb / total_mb * 100
    status = available_percent > 2.0

    return status
