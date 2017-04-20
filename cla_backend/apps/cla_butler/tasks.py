# -*- coding: utf-8 -*-
import datetime
import os

from celery import Task
import logging

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .qs_to_csv import QuerysetToCsv
from cla_eventlog.models import Log
from diagnosis.models import DiagnosisTraversal
from legalaid.models import Case, EligibilityCheck, CaseNotesHistory, Person,\
    Income, Savings, Deductions, PersonalDetails, ThirdPartyDetails, \
    AdaptationDetails


logger = logging.getLogger(__name__)


class DeleteOldData(Task):
    """
    Deletes old data that is no longer needed.

    Case data more than 2 years old is no longer needed so will be deleted.

    We also delete empty cases and data thet is not connected to anything in
    particular.
    
    Maybe faster to dump to json using
    from django.core.serializers.json import DjangoJSONEncoder
    json.dumps(list(Case.objects.all()[:100].values()), cls=DjangoJSONEncoder)
    """

    def run(self, *args, **kwargs):
        self._setup()
        self.cleanup_cases()
        self.cleanup_diagnosis()
        self.cleanup_eligibility_check()
        self.cleanup_person()
        self.cleanup_third_party_details()
        self.cleanup_personal_details()
        self.cleanup_adaptation_details()
        self.cleanup_sessions()

    def _setup(self):
        self.now = timezone.now()
        path = os.path.join(settings.TEMP_DIR, self.now.strftime('%Y%m%d'))
        self.csvwriter = QuerysetToCsv(path)

    def _delete_logs(self, qs):
        ct = ContentType.objects.get_for_model(qs.model)
        pks = qs.values_list('pk', flat=True)
        logs = Log.objects.filter(
            content_type=ct,
            object_id__in=pks
        )
        self.csvwriter.dump(logs)
        logs.delete()
        log_entries = LogEntry.objects.filter(
            content_type=ct,
            object_id__in=pks
        )
        self.csvwriter.dump(log_entries)
        log_entries.delete()

    def _delete_objects(self, qs):
        self._delete_logs(qs)

        name = qs.model.__name__
        print 'Total {name} objects: {count}'.format(
            count=qs.model.objects.all().count(),
            name=name)

        print 'Deleting {count} {name} objects'.format(
            count=qs.count(),
            name=name)

        self.csvwriter.dump(qs)
        qs.delete()

        print 'Total {name} objects: {count}'.format(
            count=qs.model.objects.all().count(),
            name=name)

    def cleanup_sessions(self):
        sessions = Session.objects.filter(
            expire_date__lte=self.now,
        )
        sessions.delete()

    def cleanup_cases(self):
        two_years = self.now - relativedelta(years=2)
        cases = Case.objects.filter(
            modified__lte=two_years,
        )
        self.cleanup_case_note_history(map(str, cases.values_list('pk', flat=True)))
        self._delete_objects(cases)

    def cleanup_case_note_history(self, pks):
        cnhs = CaseNotesHistory.objects.filter(
            pk__in=pks
        )
        self._delete_objects(cnhs)

    def cleanup_diagnosis(self):
        yesterday = self.now - datetime.timedelta(days=10)
        diags = DiagnosisTraversal.objects.filter(
            case__isnull=True,
            modified__lte=yesterday,
        )
        self._delete_objects(diags)

    def cleanup_eligibility_check(self):
        yesterday = self.now - datetime.timedelta(days=10)
        ecs = EligibilityCheck.objects.filter(
            case__isnull=True,
            modified__lte=yesterday,
        )
        self._delete_objects(ecs)

    def cleanup_person(self):
        ps = Person.objects.filter(you__isnull=True, partner__isnull=True)
        self._delete_objects(ps)
        incomes = Income.objects.filter(person__isnull=True)
        self._delete_objects(incomes)
        savings = Savings.objects.filter(person__isnull=True)
        self._delete_objects(savings)
        deductions = Deductions.objects.filter(person__isnull=True)
        self._delete_objects(deductions)

    def cleanup_personal_details(self):
        pds = PersonalDetails.objects.filter(
            case__isnull=True
        )
        self._delete_objects(pds)

    def cleanup_third_party_details(self):
        tps = ThirdPartyDetails.objects.filter(
            case__isnull=True
        )
        self._delete_objects(tps)

    def cleanup_adaptation_details(self):
        ads = AdaptationDetails.objects.filter(
            case__isnull=True
        )
        self._delete_objects(ads)
