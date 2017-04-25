# -*- coding: utf-8 -*-
import datetime
import os
import time

from celery import Task
import logging

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .qs_to_file import QuerysetToFile
from cla_eventlog.models import Log
from cla_provider.models import Feedback
from complaints.models import Complaint
from diagnosis.models import DiagnosisTraversal
from legalaid.models import Case, EligibilityCheck, CaseNotesHistory, Person,\
    Income, Savings, Deductions, PersonalDetails, ThirdPartyDetails, \
    AdaptationDetails, CaseKnowledgebaseAssignment, EODDetails, \
    EODDetailsCategory, Property
from timer.models import Timer


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

    or

    https://docs.djangoproject.com/en/1.8/topics/serialization/

    from django.core import serializers
    data = serializers.serialize("json", SomeModel.objects.all())
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
        self.filewriter = QuerysetToFile(path)

    def _delete_logs(self, qs):
        ct = ContentType.objects.get_for_model(qs.model)
        pks = map(str, qs.values_list('pk', flat=True))
        if pks:
            logs = Log.objects.filter(
                content_type_id=ct.pk,
                object_id__in=pks
            )
            self.filewriter.dump(logs)
            logs.delete()
            log_entries = LogEntry.objects.filter(
                content_type=ct,
                object_id__in=pks
            )
            self.filewriter.dump(log_entries)
            log_entries.delete()

    def _delete_objects(self, qs):
        qs = qs.order_by('pk')
        self._delete_logs(qs)

        name = qs.model.__name__
        logger.info('Total {name} objects: {count}'.format(
            count=qs.model.objects.all().count(),
            name=name))

        logger.info('Deleting {count} {name} objects'.format(
            count=qs.count(),
            name=name))
        self.filewriter.dump(qs)
        logger.info('Starting delete of %s' % name)
        start = time.time()
        qs._raw_delete(qs.db)
        logger.info('Time to delete %s: %s' % (name, time.time() - start))

        logger.info('Total {name} objects: {count}'.format(
            count=qs.model.objects.all().count(),
            name=name))

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
        pks = map(str, cases.values_list('pk', flat=True))
        from_cases = Case.objects.filter(from_case_id__in=pks)
        fpks = map(str, from_cases.values_list('pk', flat=True))
        pks += fpks
        self.cleanup_model_from_case(pks, CaseNotesHistory)
        self.cleanup_model_from_case(pks, Log)
        self.cleanup_model_from_case(pks, Feedback)
        self.cleanup_model_from_case(pks, Timer, 'linked_case', 'timer')
        self.cleanup_model_from_case(pks, CaseKnowledgebaseAssignment)
        self.cleanup_model_from_case(pks, Complaint, 'eod__case_id')
        self.cleanup_model_from_case(pks, EODDetailsCategory, 'eod_details__case_id')
        self.cleanup_model_from_case(pks, EODDetails)
        self._delete_objects(cases)
        self._delete_objects(from_cases)

    def cleanup_model_from_case(self, pks, model, attr='case_id', case_log_attr=None):
        qs = model.objects.filter(
            **{'%s__in' % attr: pks}
        )
        if case_log_attr:
            logs = Log.objects.filter(
                **{'%s__in' % case_log_attr: map(str, qs.values_list('pk', flat=True))}
            )
            self._delete_objects(logs)
        self._delete_objects(qs)

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
        pks = map(str, ecs.values_list('pk', flat=True))
        self.cleanup_model_from_ec(pks, Property)
        self._delete_objects(ecs)

    def cleanup_model_from_ec(self, pks, model, attr='eligibility_check_id'):
        qs = model.objects.filter(
            **{'%s__in' % attr: pks}
        )
        self._delete_objects(qs)

    def cleanup_person(self):
        ps = Person.objects.filter(you__isnull=True, partner__isnull=True)
        self._delete_objects(ps)
        incomes = Income.objects.filter(person__isnull=True)
        self._delete_objects(incomes)
        savings = Savings.objects.filter(
            person__isnull=True,
            eligibilitycheck__isnull=True)
        self._delete_objects(savings)
        deductions = Deductions.objects.filter(person__isnull=True)
        self._delete_objects(deductions)

    def cleanup_third_party_details(self):
        tps = ThirdPartyDetails.objects.filter(
            case__isnull=True
        )
        self._delete_objects(tps)

    def cleanup_personal_details(self):
        pds = PersonalDetails.objects.filter(
            case__isnull=True,
            thirdpartydetails__isnull=True
        )
        self._delete_objects(pds)

    def cleanup_adaptation_details(self):
        ads = AdaptationDetails.objects.filter(
            case__isnull=True
        )
        self._delete_objects(ads)
