# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.core.management.base import BaseCommand

from cla_eventlog.models import Log
from diagnosis.models import DiagnosisTraversal
from legalaid.models import Case, EligibilityCheck, CaseNotesHistory, Person,\
    Income, Savings, Deductions, PersonalDetails, ThirdPartyDetails, \
    AdaptationDetails

from ...qs_to_csv import QuerysetToCsv


MODELS = [
    Deductions,
    Income,
    Savings,
    Person,
    AdaptationDetails,
    ThirdPartyDetails,
    PersonalDetails,
    EligibilityCheck,
    DiagnosisTraversal,
    CaseNotesHistory,
    Case,
    Log,
    LogEntry,
]


class Command(BaseCommand):

    help = 'Attempts to re-load data that was deleted in the housekeeping'

    def add_arguments(self, parser):
        parser.add_argument('directory', nargs=1, type=str)

    def handle(self, *args, **options):
        d = args[0]
        path = os.path.join(settings.TEMP_DIR, d)
        csvwriter = QuerysetToCsv(path)

        for model in MODELS:
            csvwriter.load(model)
