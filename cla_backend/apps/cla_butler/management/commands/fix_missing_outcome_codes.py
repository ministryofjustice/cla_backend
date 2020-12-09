# coding=utf-8
import logging
from django.core.management.base import BaseCommand


from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
from cla_eventlog.models import Log

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "LGA-275 specific command to re-denormalize outcome codes missing from Case instances"

    def handle(self, *args, **options):
        self.re_denormalize_outcome_codes_to_cases()

    @staticmethod
    def re_denormalize_outcome_codes_to_cases():
        outcome_kwargs = {"level": LOG_LEVELS.HIGH, "type": LOG_TYPES.OUTCOME}
        outcomes_that_should_be_denormed = Log.objects.filter(**outcome_kwargs).order_by("created")  # Oldest to newest
        outcomes_missing_denormed_code = outcomes_that_should_be_denormed.filter(case__outcome_code="")
        logger.info("\nLGA-275: {} outcomes_missing_denormed_code".format(outcomes_missing_denormed_code.count()))
        for outcome in outcomes_missing_denormed_code:
            outcome.case.outcome_code = outcome.code
            outcome.case.save()
            logger.info("LGA-275: Filled missing outcome code for case {}".format(outcome.case.reference))
