import datetime

import dateutil.parser as parser

from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from cla_common.constants import CASE_STATE_CLOSED, CASE_STATE_OPEN
from legalaid.constants import CASELOGTYPE_SUBTYPES

from model_mommy import mommy

from legalaid.models import CaseLog

from ..forms import ProviderCaseClosureReportForm, \
    OperatorCaseClosureReportForm


def make_recipe(model_name, **kwargs):
    return mommy.make_recipe('legalaid.tests.%s' % model_name, **kwargs)


def cla_provider_make_recipe(model_name, **kwargs):
    return mommy.make_recipe('cla_provider.tests.%s' % model_name, **kwargs)


class ProviderCaseClosureReportFormTestCase(TestCase):
    def test_rows(self):
        """
            Search:
                Provider pk: 1
                date from: 02/04/2014
                date to: 15/04/2014

            Cases / Outcomes:
                ref '1': provider 1, closure date (16/04/2014 00:00) => excluded
                ref '2': provider 1, closure date (15/04/2014 23:59) => included
                ref '3': provider 2, closure date (02/04/2014 00:01) => excluded
                ref '4': provider 1, closure date (02/04/2014 00:01) => included
                ref '5': provider 1, closure date (02/04/2014 00:00) => included
                ref '6': provider 1, closure date (01/04/2014 23:59) => excluded
                ref '7': provider 1, no closure => excluded

            Result:
                [5, 4, 2] - [Total: 3]

        """
        providers = cla_provider_make_recipe('provider', active=True, _quantity=2)

        def create_db_record(case_ref, closure_date, provider, case_state=CASE_STATE_CLOSED):
            case_outcome = make_recipe('case_log',
                logtype__case_state=case_state,
                case__provider=provider,
                case__reference=case_ref,
                logtype__code='outcome_%s' % case_ref,
                logtype__subtype=CASELOGTYPE_SUBTYPES.OUTCOME,
                case__eligibility_check__category__name='Category_%s' % case_ref
            )
            closure_date = parser.parse(closure_date)
            case_outcome.__class__.objects.filter(pk=case_outcome.pk).update(
                created=closure_date.replace(tzinfo=timezone.utc)
            )

        create_db_record('1', '2014-04-16T01:00', providers[0])
        create_db_record('2', '2014-04-15T00:59', providers[0])
        create_db_record('3', '2014-04-02T01:01', providers[1])
        create_db_record('4', '2014-04-02T01:01', providers[0])
        create_db_record('5', '2014-04-02T01:00', providers[0])
        create_db_record('6', '2014-04-01T00:59', providers[0])
        create_db_record('7', '2014-04-01T00:59', providers[0], case_state=CASE_STATE_OPEN)


        # form, non-empty result
        form = ProviderCaseClosureReportForm({
            'provider': providers[0].pk,
            'date_from': datetime.date(2014, 4, 2),
            'date_to': datetime.date(2014, 4, 15)
        })

        self.assertTrue(form.is_valid())

        rows = list(form.get_rows())
        self.assertEqual(rows,
            [
                [u'5', '02/04/2014 01:00', u'outcome_5', u'Category_5'],
                [u'4', '02/04/2014 01:01', u'outcome_4', u'Category_4'],
                [u'2', '15/04/2014 00:59', u'outcome_2', u'Category_2'],
                [],
                ['Total: 3']
            ]
        )

        # form, empty results
        form = ProviderCaseClosureReportForm({
            'provider': providers[0].pk,
            'date_from': datetime.date(2014, 4, 19),
            'date_to': datetime.date(2014, 4, 20)
        })

        self.assertTrue(form.is_valid())

        rows = list(form.get_rows())
        self.assertEqual(rows,
            [
                [],
                ['Total: 0']
            ]
        )

    def test_get_headers(self):
        form = ProviderCaseClosureReportForm()

        self.assertEqual(
            form.get_headers(),
            ['Case #', 'Closure Date', 'Outcome Code', 'Law Categories']
        )



class OperatorCaseClosureReportFormTestCase(TestCase):
    def test_rows(self):
        """
            Search:
                date from: 02/04/2014
                date to: 15/04/2014

            Cases / Outcomes:
                ref '1': provider 1, assign date (16/04/2014 00:00) => excluded
                ref '2': provider 1, assign date (15/04/2014 23:59) => included
                ref '3': provider 2, assign date (02/04/2014 00:01) => excluded
                ref '4': provider 1, assign date (02/04/2014 00:01) => included
                ref '5': provider 1, assign date (02/04/2014 00:00) => included
                ref '6': provider 1, assign date (01/04/2014 23:59) => excluded
                ref '7': provider 1, no assign => excluded

            Result:
                [5, 4, 2] - [Total: 3] - [Average: 100]

        """
        providers = cla_provider_make_recipe('provider', active=True, _quantity=2)
        caselogtype = make_recipe('logtype', code='ASSIGN', subtype=CASELOGTYPE_SUBTYPES.SYSTEM)

        # form, empty results
        form = OperatorCaseClosureReportForm({
            'date_from': datetime.date(2014, 4, 19),
            'date_to': datetime.date(2014, 4, 20)
        })

        self.assertTrue(form.is_valid())

        rows = list(form.get_rows())
        self.assertEqual(rows,
                         [
                             [],
                             ['Total: 0'],
                             ['Average Duration: 0']
                         ]
        )



        def create_db_record(case_ref, assign_date, provider, case_state=CASE_STATE_OPEN):
            assign_date = parser.parse(assign_date).replace(tzinfo=timezone.utc)
            case_outcome = make_recipe('case_log',
                                       logtype__case_state=case_state,
                                       case__provider=provider,
                                       case__reference=case_ref,
                                       case__created=assign_date - datetime.timedelta(seconds=200),
                                       created=assign_date - datetime.timedelta(seconds=20),
                                       logtype=caselogtype,
                                       case__eligibility_check__category__name='Category_%s' % case_ref
            )
            case_outcome.__class__.objects.filter(pk=case_outcome.pk).update(
                created=assign_date.replace(tzinfo=timezone.utc)
            )

        create_db_record('1', '2014-04-16T01:00', providers[0])
        create_db_record('2', '2014-04-15T00:59', providers[0])
        create_db_record('3', '2014-04-02T01:01', providers[1])
        create_db_record('4', '2014-04-02T01:01', providers[0])
        create_db_record('5', '2014-04-02T01:00', providers[0])
        create_db_record('6', '2014-04-01T00:59', providers[0])
        create_db_record('7', '2014-04-01T00:59', providers[0])


        # form, non-empty result
        form = OperatorCaseClosureReportForm({
            'date_from': datetime.date(2014, 4, 2),
            'date_to': datetime.date(2014, 4, 15)
        })

        self.assertTrue(form.is_valid())

        self.maxDiff = None

        rows = list(form.get_rows())
        self.assertEqual(rows,
                         [
                             [u'5', '02/04/2014 00:56', '02/04/2014 01:00', 200, u'ASSIGN', u'Name1'],
                             [u'3', '02/04/2014 00:57', '02/04/2014 01:01', 200, u'ASSIGN', u'Name2'],
                             [u'4', '02/04/2014 00:57', '02/04/2014 01:01', 200, u'ASSIGN', u'Name1'],
                             [u'2', '15/04/2014 00:55', '15/04/2014 00:59', 200, u'ASSIGN', u'Name1'],
                             [],
                             ['Total: 4'],
                             ['Average Duration: 200']
                         ]
        )


    def test_get_headers(self):
        form = OperatorCaseClosureReportForm()

        self.assertEqual(
            form.get_headers(),
           ['Case #', 'Call Started', 'Call Assigned', 'Duration (sec)','Outcome Code', 'To Provider']
        )
