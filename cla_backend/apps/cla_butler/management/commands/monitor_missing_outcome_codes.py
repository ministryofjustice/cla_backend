# coding=utf-8
import logging
from django.core.management.base import BaseCommand

from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
from cla_eventlog.models import Log
from legalaid.models import Case

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "LGA-275 specific monitoring command. Count and alert when outcome codes expected to be "
        "denormalized to Case instances are missing"
    )

    def handle(self, *args, **options):
        self.check_for_missing_outcome_codes()

    @staticmethod
    def check_for_missing_outcome_codes():
        outcomes_that_should_be_denormed = Log.objects.filter(level=LOG_LEVELS.HIGH, type=LOG_TYPES.OUTCOME)
        outcomes_missing_denormed_code = outcomes_that_should_be_denormed.filter(case__outcome_code="")
        cases_to_re_denorm = Case.objects.filter(log__in=outcomes_missing_denormed_code)

        if cases_to_re_denorm.exists():
            case_references = cases_to_re_denorm.values_list("reference", flat=True)
            logger.error(
                "LGA-275 investigation. Cases found with outcome code missing; "
                "value expected to be denormalized from log. Number of cases: {}\nReferences: {}".format(
                    len(case_references), case_references
                )
            )
        else:
            logger.info("LGA-275 No cases found missing denormalized outcome codes")
