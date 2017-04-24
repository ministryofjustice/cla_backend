# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.core.management.base import BaseCommand

from cla_eventlog.models import Log
from cla_provider.models import Feedback
from complaints.models import Complaint
from diagnosis.models import DiagnosisTraversal
from legalaid.models import Case, EligibilityCheck, CaseNotesHistory, Person,\
    Income, Savings, Deductions, PersonalDetails, ThirdPartyDetails, \
    AdaptationDetails, CaseKnowledgebaseAssignment, EODDetails, \
    EODDetailsCategory, Property
from timer.models import Timer

from ...qs_to_file import QuerysetToFile


MODELS = [
    Deductions,
    Income,
    Savings,
    Person,
    AdaptationDetails,
    PersonalDetails,
    ThirdPartyDetails,
    EligibilityCheck,
    Property,
    DiagnosisTraversal,
    Case,
    EODDetails,
    EODDetailsCategory,
    Complaint,
    CaseKnowledgebaseAssignment,
    Timer,
    Feedback,
    CaseNotesHistory,
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
        filewriter = QuerysetToFile(path)

        for model in MODELS:
            print model.__name__
            filewriter.load(model)
