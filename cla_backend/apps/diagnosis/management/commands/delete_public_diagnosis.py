# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import NoArgsCommand
from django.utils import timezone

from diagnosis.models import DiagnosisTraversal


class Command(NoArgsCommand):

    help = 'Deletes public diagnosis that are more than a day old'

    def handle_noargs(self, *args, **options):
        self.stdout.write('Total DiagnosisTraversal objects: %s' %
                    DiagnosisTraversal.objects.all().count())
        yesterday = timezone.now() - datetime.timedelta(days=1)
        diags = DiagnosisTraversal.objects.filter(
            case__isnull=True,
            modified__lte=yesterday,
        )
        self.stdout.write('Deleting %s DiagnosisTraversal objects' % diags.count())

        diags.delete()

        self.stdout.write('Total DiagnosisTraversal objects: %s' %
                    DiagnosisTraversal.objects.all().count())

