# coding=utf-8
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask


def create_crontab_from_datetime(dt):
    print (dt.tzinfo)
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=dt.minute,
        hour=dt.hour,
        day_of_month=dt.day,
        month_of_year=dt.month,
        timezone=str(dt.tzinfo)
    )
    return schedule


def schedule_notification(instance):
    start_name = "%s - start" % instance.pk
    end_name = "%s - end" % instance.pk
    PeriodicTask.objects.filter(name=start_name).delete()
    PeriodicTask.objects.filter(name=end_name).delete()
    if instance.start_time > timezone.now():
        PeriodicTask.objects.create(
            crontab=create_crontab_from_datetime(instance.start_time),
            name=start_name,
            task='notifications.tasks.send_notifications',
            # one_off=True,
        )
    PeriodicTask.objects.create(
        crontab=create_crontab_from_datetime(instance.end_time),
        name=end_name,
        task='notifications.tasks.send_notifications',
        # one_off=True,
    )


def send_notifications_to_users(sender, instance, **kwargs):
    schedule_notification(instance)
