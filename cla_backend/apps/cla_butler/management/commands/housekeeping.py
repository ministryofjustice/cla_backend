# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from cla_eventlog.models import Log
from diagnosis.models import DiagnosisTraversal
from legalaid.models import Case, EligibilityCheck


class Command(BaseCommand):

    help = 'Deletes public diagnosis that are more than a day old'

    def handle(self, *args, **options):
        self._setup()
        self.cleanup_diagnosis()
        self.cleanup_eligibility_check()
        self.cleanup_cases()

    def _setup(self):
        self.now = timezone.now()

    def _delete_logs(self, qs):
        ct = ContentType.objects.get_for_model(qs.model)
        logs = Log.objects.filter(
            content_type=ct,
            object_id__in=[i.pk for i in qs]
        )
        logs.delete()
        log_entries = LogEntry.objects.filter(
            content_type=ct,
            object_id__in=[i.pk for i in qs]
        )
        log_entries.delete()

    def _delete_objects(self, qs):
        self._delete_logs(qs)

        name = qs.model.__name__
        self.stdout.write('Total {name} objects: {count}'.format(
            count=qs.model.objects.all().count(),
            name=name))

        self.stdout.write('Deleting {count} {name} objects'.format(
            count=qs.count(),
            name=name))

        qs.delete()

        self.stdout.write('Total {name} objects: {count}'.format(
            count=qs.model.objects.all().count(),
            name=name))

    def cleanup_diagnosis(self, *args, **options):
        yesterday = self.now - datetime.timedelta(days=1)
        diags = DiagnosisTraversal.objects.filter(
            case__isnull=True,
            modified__lte=yesterday,
        )
        self._delete_objects(diags)

    def cleanup_eligibility_check(self):
        yesterday = self.now - datetime.timedelta(days=1)
        ecs = EligibilityCheck.objects.filter(
            case__isnull=True,
            modified__lte=yesterday,
        )
        self._delete_objects(ecs)

    def cleanup_cases(self):
        two_years = self.now - relativedelta(years=2)
        cases = Case.objects.filter(
            modified__lte=two_years,
        )
        self._delete_objects(cases)
