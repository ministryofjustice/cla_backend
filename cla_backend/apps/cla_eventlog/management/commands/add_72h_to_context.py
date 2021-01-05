# coding=utf-8
from django.core.management.base import BaseCommand
from cla_eventlog.models import Log
from cla_common import call_centre_availability
from legalaid.utils.sla import get_sla_time
from django.utils import timezone


class CallCentreAvailabilityHistoricCurrentDateTime(object):
    def __init__(self, start_time):
        self.start_time = start_time
        self.orig_current_datetime = call_centre_availability.current_datetime

    def get_current_datetime(self):
        now = self.start_time
        if timezone.is_naive(now):
            return now
        else:
            return timezone.make_naive(now, self.start_time.tzinfo)

    def __enter__(self):
        call_centre_availability.current_datetime = self.get_current_datetime

    def __exit__(self, exc_type, exc_val, exc_tb):
        call_centre_availability.current_datetime = self.orig_current_datetime


class Command(BaseCommand):
    help = "Add 72 working hours to the event_log context to be used for sla reporting."

    def handle(self, *args, **options):
        logs = self.get_logs()
        for log in logs:
            context = log.context
            context["sla_72h"] = self.get_72_working_hours_sla(log.case.requires_action_at)
            self.stdout.write(
                "Updating {} from requires_action_at {} to sla_72h {}".format(
                    log, log.case.requires_action_at, log.context["sla_72h"]
                )
            )
            # Do update at sql level to avoid affecting auto updating fields and model signals
            Log.objects.filter(pk=log.pk).update(context=context)

    def get_72_working_hours_sla(self, start_time):
        start_time = timezone.localtime(start_time)
        sla2_minutes = 72 * 60
        with CallCentreAvailabilityHistoricCurrentDateTime(start_time):
            return get_sla_time(start_time, sla2_minutes)

    def get_logs(self):
        return Log.objects.filter(code="CB1", type="outcome").exclude(context__contains="sla_72h")
