# coding=utf-8
import json
from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.db import connection

from legalaid.utils import diversity
from legalaid.models import PersonalDetails, ThirdPartyDetails, EligibilityCheck, Case, CaseNotesHistory, EODDetails
from complaints.models import Complaint


OBFUSCATED_FIELDS = {
    PersonalDetails: {
        "full_name": "Fullname Obfuscated",
        "postcode": "SW1H 9AJ",
        "street": "102 Petty France",
        "mobile_phone": "55555555555",
        "home_phone": "55555555555",
        "email": "cla-test@digital.justice.gov.uk",
        "date_of_birth": "1963-03-16",
        "ni_number": "SD-156-266",
        "diversity": {"gender": "", "ethnicity": "", "religion": "", "sexual_orientation": "", "disability": ""},
        "search_field": "",
    },
    ThirdPartyDetails: {
        "pass_phrase": "obfuscate",
        "reason": "Reason obfuscated",
        "personal_relationship": "Data obfuscated",
        "personal_relationship_note": "Data obfuscated",
        "organisation_name": "Data obfuscated",
    },
    EligibilityCheck: {"notes": "Data obfuscated"},
    Case: {"notes": "Data obfuscated", "provider_notes": "Data obfuscated", "search_field": ""},
    CaseNotesHistory: {"operator_notes": "Data obfuscated", "provider_notes": "Data obfuscated"},
    EODDetails: {"notes": "Data obfuscated"},
    Complaint: {"description": "Data obfuscated"},
}


class Command(NoArgsCommand):

    help = "Obfuscate all sensitive data in the database"

    def handle_noargs(self, *args, **kwargs):
        if settings.CLA_ENV != "prod":
            with connection.cursor() as cursor:
                for model, field_names in OBFUSCATED_FIELDS.items():
                    for field_name, value in field_names.items():
                        self._obfuscate_field(cursor, model, field_name, value)

    def _obfuscate_field(self, cursor, model, field_name, value):
        if field_name == "diversity":
            value = "pgp_pub_encrypt('{diversity}', dearmor('{key}'))".format(
                diversity=json.dumps(value), key=diversity.get_public_key()
            )
        else:
            value = "'%s'" % value

        query = "UPDATE %s SET %s = %s" % (model._meta.db_table, field_name, value)

        cursor.execute(query)
        if field_name != "diversity":
            self.stdout.write(query)
