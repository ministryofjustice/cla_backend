# -*- coding: utf-8 -*-
import datetime

from django.db.models import Q
from django.core.management.base import NoArgsCommand
from django.utils import timezone

from diagnosis.models import DiagnosisTraversal
from legalaid.models import Case, EligibilityCheck


class Command(NoArgsCommand):

    help = 'Deletes public diagnosis that are more than a day old'

    def handle_noargs(self, *args, **options):
        self.cleanup_diagnosis()

    def cleanup_diagnosis(self, *args, **options):
        self.stdout.write('Total DiagnosisTraversal objects: {count}'.format(
            count=DiagnosisTraversal.objects.all().count()))
        yesterday = timezone.now() - datetime.timedelta(days=1)
        diags = DiagnosisTraversal.objects.filter(
            case__isnull=True,
            modified__lte=yesterday,
        )
        self.stdout.write('Deleting %s DiagnosisTraversal objects'.format(
            count=diags.count()))

        diags.delete()

        self.stdout.write('Total DiagnosisTraversal objects: {count}'.format(
            count=DiagnosisTraversal.objects.all().count()))

    def cleanup_cases(self):
        for case in Case.objects.all():
            pass

    def cleanup_eligibility_check(self):
        for ec in EligibilityCheck.objects.all():
            pass
