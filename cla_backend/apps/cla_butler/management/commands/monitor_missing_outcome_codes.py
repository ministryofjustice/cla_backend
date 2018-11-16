# coding=utf-8
import logging
from django.core.management.base import BaseCommand

from cla_butler.stack import is_first_instance, InstanceNotInAsgException, StackException

from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
from cla_eventlog.models import Log
from legalaid.models import Case

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Count and alert when outcome codes denormalized to Case instances are missing'

    def handle(self, *args, **options):
        if self.should_run_housekeeping(**options):
            self.check_for_missing_outcome_codes()
        else:
            self.stdout.write('Not doing housekeeping because running on secondary instance')

    @staticmethod
    def check_for_missing_outcome_codes():
        outcomes_that_should_be_denormed = Log.objects.filter(level=LOG_LEVELS.HIGH, type=LOG_TYPES.OUTCOME)
        outcomes_missing_denormed_code = outcomes_that_should_be_denormed.filter(case__outcome_code='')
        outcomes_missing_denormed_code_pks = outcomes_missing_denormed_code.values_list('id', flat=True)
        cases_to_re_denorm = Case.objects.filter(outcome_code='', outcome_code_id__isnull=False,
                                                 log_set__id__in=outcomes_missing_denormed_code_pks)

        if cases_to_re_denorm.exists():
            case_references = cases_to_re_denorm.value_list('reference', flat=True)
            n = len(case_references)
            logger.warning('Cases found missing denormalized outcome codes: {}\n'
                           'References: {}'.format(n, case_references))
        else:
            logger.info('No cases found missing denormalized outcome codes')

    @staticmethod
    def should_run_housekeeping(**options):
        if options.get('force', False):
            return True
        try:
            return is_first_instance()
        except InstanceNotInAsgException:
            logger.info('EC2 instance not in an ASG')
            return True
        except StackException:
            logger.info('Not running on EC2 instance')
            return True
