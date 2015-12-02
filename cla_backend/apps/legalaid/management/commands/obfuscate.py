# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.core import settings

from legalaid.models import PersonalDetails, ThirdPartyDetails, \
    EligibilityCheck, Case, CaseNoteHistory, EODDetails, Complaint


OBFUSCATED_FIELDS = {
    PersonalDetails: {
        'full_name': 'Fullname Obfuscated',
        'postcode': 'SW1H 9AJ',
        'street': '102 Petty France',
        'mobile_phone': '55555555555',
        'home_phone': '55555555555',
        'email': 'cla-test@digital.justice.gov.uk',
        'date_of_birth': '1963-03-16',
        'ni_number': 'SD-156-266',
        'diversity': {},
        'search_field': '',
    },

    ThirdPartyDetails: {
        'pass_phrase': 'obfuscate',
        'reason': 'Reason obfuscated',
        'personal_relationship': 'Data obfuscated',
        'personal_relationship_note': 'Data obfuscated',
        'organisation_name': 'Data obfuscated',
    },

    EligibilityCheck: {
        'notes': 'Data obfuscated',
    },

    Case: {
        'notes': 'Data obfuscated',
        'provider_notes': 'Data obfuscated',
        'search_field': '',
    },

    CaseNoteHistory: {
        'operator_notes': 'Data obfuscated',
        'provider_notes': 'Data obfuscated',
    },

    EODDetails: {
        'notes': 'Data obfuscated',
    },

    Complaint: {
        'description': 'Data obfuscated',
    },
}


class Command(NoArgsCommand):

    help = ('Obfuscate all sensitive data in the database')

    def handle_noargs(self, *args, **kwargs):
        for model, field_names in OBFUSCATED_FIELDS.items():
            for instance in models.objects.all():
                for field_name in field_names:
                    self._obfuscate_field(instance, field_name)

    def _obfuscate_field(self, instance, field_name):
        pass



