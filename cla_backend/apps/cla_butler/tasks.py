# coding=utf-8
import datetime
import os

from dateutil.relativedelta import relativedelta
import logging
import time

from celery import Task
from cla_butler.constants import delete_option_three_years, delete_option_no_personal_details
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from oauth2_provider.models import AccessToken

from checker.models import ReasonForContactingCategory, ReasonForContacting
from cla_auditlog.models import AuditLog
from cla_eventlog.models import Log
from cla_provider.models import Feedback
from complaints.models import Complaint
from diagnosis.models import DiagnosisTraversal
from legalaid.models import (
    Case,
    EligibilityCheck,
    CaseNotesHistory,
    Person,
    Income,
    Savings,
    Deductions,
    PersonalDetails,
    ThirdPartyDetails,
    AdaptationDetails,
    CaseKnowledgebaseAssignment,
    EODDetails,
    EODDetailsCategory,
    Property,
)
from timer.models import Timer
from legalaid.utils import diversity
from cla_butler.models import DiversityDataCheck, ACTION, STATUS


logger = logging.getLogger(__name__)


def get_pks(qs):
    return [str(pk) for pk in qs.values_list("pk", flat=True)]


class DeleteOldData(Task):
    """
    Deletes old data that is no longer needed.

    We also delete empty cases and data thet is not connected to anything in
    particular.
    """

    OUTCOME_CODES = ["COI", "MIS", "REOPEN", "SPOP"]

    def __init__(self, *args, **kwargs):
        self._setup()

    def run(self, delete_option, *args, **kwargs):
        self.cleanup_cases(delete_option)
        self.cleanup_diagnosis()
        self.cleanup_eligibility_check()
        self.cleanup_person()
        self.cleanup_third_party_details()
        self.cleanup_personal_details()
        self.cleanup_adaptation_details()
        self.cleanup_sessions()
        self.cleanup_access_tokens()

    def _setup(self):
        self.now = timezone.now()

    def get_three_year_old_cases(self):
        """
        This gets cases which are over three years old and have a specific
        outcome code indicating its closed.
        """
        three_years = self.now - relativedelta(years=3)

        return Case.objects.filter(modified__lte=three_years).exclude(outcome_code__in=self.OUTCOME_CODES)

    def get_cases_without_personal_details(self):
        """
        Returns data older than 2 weeks. Queryset of personal detail's id that are none
        and do not have notes and provider details
        """

        two_weeks = self.now - relativedelta(weeks=2)

        return (
            Case.objects.filter(modified__lte=two_weeks)
            .filter(personal_details_id__exact=None)
            .filter(notes__exact=u"")
            .filter(provider_notes__exact=u"")
        )

    def _delete_logs(self, qs):
        ct = ContentType.objects.get_for_model(qs.model)
        pks = get_pks(qs)
        if pks:
            logs = Log.objects.filter(content_type_id=ct.pk, object_id__in=pks)
            logs.delete()
            log_entries = LogEntry.objects.filter(content_type=ct, object_id__in=pks)
            log_entries.delete()

    def _delete_objects(self, qs):
        qs = qs.order_by("pk")
        self._delete_logs(qs)

        name = qs.model.__name__
        logger.info("Total {name} objects: {count}".format(count=qs.model.objects.all().count(), name=name))

        logger.info("Deleting {count} {name} objects".format(count=qs.count(), name=name))
        logger.info("Starting delete of {name}".format(name=name))
        start = time.time()
        qs._raw_delete(qs.db)
        logger.info("Time to delete {name}: {time}".format(name=name, time=time.time() - start))

        logger.info("Total {name} objects: {count}".format(count=qs.model.objects.all().count(), name=name))

    def cleanup_sessions(self):
        sessions = Session.objects.filter(expire_date__lte=self.now)
        sessions.delete()

    def cleanup_access_tokens(self):
        tokens = AccessToken.objects.filter(expires__lte=self.now)
        tokens.delete()

    def cases_for_deletion(self, delete_option):
        if delete_option == delete_option_three_years:
            return self.get_three_year_old_cases()
        elif delete_option == delete_option_no_personal_details:
            return self.get_cases_without_personal_details()
        else:
            raise Exception("No method of deletion, no cases have been deleted")

    def cleanup_cases(self, delete_option):
        cases = self.cases_for_deletion(delete_option)
        pks = get_pks(cases)
        from_cases = Case.objects.filter(from_case_id__in=pks)
        fpks = get_pks(from_cases)
        pks += fpks
        self.cleanup_model_from_case(pks, CaseNotesHistory)
        self.cleanup_model_from_case(pks, Log)
        self.cleanup_model_from_case(pks, Feedback)
        self.cleanup_model_from_case(pks, Timer, "linked_case", "timer")
        self.cleanup_model_from_case(pks, CaseKnowledgebaseAssignment)
        self.cleanup_audit(pks)
        self.cleanup_model_from_case(pks, Complaint, "eod__case_id")
        self.cleanup_model_from_case(pks, EODDetailsCategory, "eod_details__case_id")
        self.cleanup_model_from_case(pks, EODDetails)
        self.cleanup_model_from_case(pks, ReasonForContactingCategory, "reason_for_contacting__case_id")
        self.cleanup_model_from_case(pks, ReasonForContacting)
        self._delete_objects(from_cases)
        self._delete_objects(cases)

    def cleanup_model_from_case(self, pks, model, attr="case_id", case_log_attr=None):
        attr_in = "{attribute}__in".format(attribute=attr)
        criteria = {attr_in: pks}
        qs = model.objects.filter(**criteria)
        if case_log_attr:
            log_pks = get_pks(qs)
            log_attr_in = "{attribute}__in".format(attribute=case_log_attr)
            log_criteria = {log_attr_in: log_pks}
            logs = Log.objects.filter(**log_criteria)
            self._delete_objects(logs)
        self._delete_objects(qs)

    def cleanup_diagnosis(self):
        yesterday = self.now - datetime.timedelta(days=10)
        diags = DiagnosisTraversal.objects.filter(case__isnull=True, modified__lte=yesterday)
        self._delete_objects(diags)

    def cleanup_eligibility_check(self):
        yesterday = self.now - datetime.timedelta(days=10)
        ecs = EligibilityCheck.objects.filter(case__isnull=True, modified__lte=yesterday)
        pks = get_pks(ecs)
        self.cleanup_model_from_ec(pks, Property)
        self._delete_objects(ecs)

    def cleanup_model_from_ec(self, pks, model, attr="eligibility_check_id"):
        attr_in = "{attribute}__in".format(attribute=attr)
        criteria = {attr_in: pks}
        qs = model.objects.filter(**criteria)
        self._delete_objects(qs)

    def cleanup_person(self):
        ps = Person.objects.filter(you__isnull=True, partner__isnull=True)
        self._delete_objects(ps)
        incomes = Income.objects.filter(person__isnull=True)
        self._delete_objects(incomes)
        savings = Savings.objects.filter(person__isnull=True, eligibilitycheck__isnull=True)
        self._delete_objects(savings)
        deductions = Deductions.objects.filter(person__isnull=True)
        self._delete_objects(deductions)

    def cleanup_third_party_details(self):
        tps = ThirdPartyDetails.objects.filter(case__isnull=True)
        self._delete_objects(tps)

    def cleanup_personal_details(self):
        pds = PersonalDetails.objects.filter(case__isnull=True, thirdpartydetails__isnull=True)
        PersonalDetails.contact_for_research_methods.through.objects.filter(
            personaldetails_id__in=pds.values_list("pk", flat=True)
        ).delete()

        # This deletes any DiversityDataCheck entries which have the PersonalDetails ID as a foreign key,
        # failing to delete these entries first results in an IntegrityError as DiversityDataCheck would contain
        # a non-existant PersonalDetails foreign key.
        DiversityDataCheck.objects.filter(personal_details_id__in=pds.values_list("pk", flat=True)).delete()

        self._delete_objects(pds)

    def cleanup_adaptation_details(self):
        ads = AdaptationDetails.objects.filter(case__isnull=True)
        self._delete_objects(ads)

    def cleanup_audit(self, pks):
        # Deleting case audit logs
        audit_logs = AuditLog.objects.filter(case__in=pks)
        audit_logs.delete()
        # Deleting complaint audit logs
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)
        audit_logs = AuditLog.objects.filter(complaint__in=case_complaints)
        audit_logs.delete()


class DiversityDataCheckTask(Task):
    def run(self, passphrase, start, end, description, *args, **kwargs):
        items = DiversityDataCheck.get_personal_details_with_diversity_data()[start:end]
        logger.info(description)
        for item in items:
            try:
                diversity.load_diversity_data(item.pk, passphrase)
                status = STATUS.OK
                detail = None
            except Exception as e:
                status = STATUS.FAIL
                detail = str(e)
            DiversityDataCheck.objects.get_or_create(
                personal_details_id=item.pk, action=ACTION.CHECK, defaults={"detail": detail, "status": status}
            )


class DiversityDataReencryptTask(Task):
    def run(self, passphrase_old, ids):
        previous_key = os.environ["PREVIOUS_DIVERSITY_PRIVATE_KEY"]
        for item in ids:
            if DiversityDataCheck.objects.filter(personal_details_id=item, action=ACTION.REENCRYPT).count():
                logger.info("Diversity data re-encryption: {} has already been re-encrypted. Skipping".format(item))
                continue
            try:
                logger.info("Diversity data re-encryption: Re-encrypting {}".format(item))
                diversity.reencrypt(item, previous_key, passphrase_old)
                status = STATUS.OK
                detail = None
            except Exception as e:
                status = STATUS.FAIL
                detail = str(e)
            logger.info("Diversity data re-encryption: {} - {}".format(status, detail))
            DiversityDataCheck.objects.create(
                personal_details_id=item, action=ACTION.REENCRYPT, detail=detail, status=status
            )
