# -*- coding: utf-8 -*-
import datetime
import warnings
from django.core.management.base import BaseCommand

from cla_common.constants import CASE_SOURCE
from cla_common.constants import ELIGIBILITY_STATES, DIAGNOSIS_SCOPE
from diagnosis.models import DiagnosisTraversal
from django.db.models import Q
from legalaid.models import Case, EligibilityCheck

warnings.showwarning = lambda *x: None


class Command(BaseCommand):
    help = "Prints out performance stats, nothing else."

    def _get_cases(self, source=None):
        qs = Case.objects.filter(created__gte=self.from_time, created__lte=self.to_time)
        if source:
            qs = qs.filter(source=source)
        return qs

    def _get_eligibility_checks(self):
        return EligibilityCheck.objects.filter(
            Q(case__isnull=True) | Q(case__source="WEB"),
            # notes__contains='User selected',
            created__gte=self.from_time,
            created__lte=self.to_time,
        )

    def _get_diagnosis_traversals(self):
        return DiagnosisTraversal.objects.filter(
            Q(case__isnull=True) | Q(case__source="WEB"),
            Q(nodes__contains='"heading"') | Q(nodes__isnull=True),
            created__gte=self.from_time,
            created__lte=self.to_time,
        )

    def _date_to_datetime(self, d):
        return datetime.datetime.combine(d, datetime.time(0, 0, 0, 0))

    def _parse_date(self, date_string):
        d = datetime.date(*[int(n) for n in date_string.split("-")])
        return self._date_to_datetime(d)

    def handle(self, *args, **options):
        self.from_time = (
            self._parse_date(args[0])
            if len(args) >= 1
            else self._date_to_datetime(datetime.date.today() - datetime.timedelta(weeks=4))
        )
        self.to_time = self._parse_date(args[1]) if len(args) >= 2 else self._date_to_datetime(datetime.date.today())

        self.stdout.write("\n\nNON DIGITAL:")
        self.stdout.write("-------")
        total_non_digital = 0
        for source, name in CASE_SOURCE:
            if source != "WEB":
                cases = self._get_cases(source)
                count = cases.count()
                total_non_digital += count
                self.stdout.write("%s: %s" % (source, count))

        self.stdout.write("\n\nDIGITAL:")
        self.stdout.write("-------")

        # Started
        scopes = self._get_diagnosis_traversals()
        self.stdout.write("Scopes started: %s" % (scopes.count()))

        # Out of scope
        scopes = self._get_diagnosis_traversals().filter(state=DIAGNOSIS_SCOPE.INSCOPE)
        self.stdout.write("Inscope: %s" % (scopes.count()))

        # Out of scope
        scopes = self._get_diagnosis_traversals().filter(state=DIAGNOSIS_SCOPE.OUTOFSCOPE)
        self.stdout.write("Out of scope: %s" % (scopes.count()))

        # Scope unknown
        scopes = self._get_diagnosis_traversals().filter(state=DIAGNOSIS_SCOPE.UNKNOWN)
        self.stdout.write("Scope unknown: %s" % (scopes.count()))

        # Digital eligibility checks started
        eligibility_checks = self._get_eligibility_checks()
        self.stdout.write("Eligibility checks started: %s" % eligibility_checks.count())

        eligibility_checks = self._get_eligibility_checks().filter(state=ELIGIBILITY_STATES.NO)
        self.stdout.write("Ineligible eligibility checks: %s" % eligibility_checks.count())

        eligibility_checks = self._get_eligibility_checks().filter(state=ELIGIBILITY_STATES.YES)
        self.stdout.write("Eligible eligibility checks: %s" % eligibility_checks.count())

        # Eligible people
        cases = self._get_cases(source="WEB").filter(eligibility_check__state=ELIGIBILITY_STATES.YES)
        self.stdout.write("Eligible cases: %s" % cases.count())

        # Ineligible people
        cases = self._get_cases(source="WEB").filter(eligibility_check__state=ELIGIBILITY_STATES.NO)
        self.stdout.write("Inligible cases: %s" % cases.count())

        # People with a valid outcome
        cases = self._get_cases(source="WEB").filter(
            ~Q(eligibility_check__state=ELIGIBILITY_STATES.UNKNOWN)
            | Q(
                Q(eligibility_check__state=ELIGIBILITY_STATES.UNKNOWN)
                & Q(eligibility_check__property_set__share__isnull=True)
            )
        )

        ecs = self._get_eligibility_checks().filter(Q(state=ELIGIBILITY_STATES.NO) & Q(case__isnull=True))
        diags = self._get_diagnosis_traversals().filter(Q(case__isnull=True) & Q(state=DIAGNOSIS_SCOPE.OUTOFSCOPE))
        self.stdout.write("Complete Transactions: %s" % (cases.count() + ecs.count() + diags.count()))

        # Assisted digital - click contact me
        cases = self._get_cases("WEB").filter(
            Q(eligibility_check__state=ELIGIBILITY_STATES.UNKNOWN)
            | Q(eligibility_check__isnull=True)
            & ~Q(
                Q(eligibility_check__state=ELIGIBILITY_STATES.UNKNOWN)
                & Q(eligibility_check__property_set__share__isnull=True)
            )
        )
        self.stdout.write("Assisted digital: %s" % cases.count())

        self.stdout.write("\n\nEND\n\n")
