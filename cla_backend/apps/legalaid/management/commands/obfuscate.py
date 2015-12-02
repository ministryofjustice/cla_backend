# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    """
    Obfuscate all sensitive data in db


    Personal details:
        full_name
        postcode
        street
        mobile_phone
        home_phone
        email
        date_of_birth
        ni_number
        diversity
        search_field

    Third Party details:
        pass_phrase
        reason
        personal_relationship
        personal_relationship_note
        organisation_name

    Eligibility check:
        notes

    Case:
        notes
        provider_notes
        search_field

    Case Note History:
        operator_notes
        provider_notes

    EOD details:
        notes

    Complaint:
        description

    """

    help = ('Obfuscate all sensitive data in the database')

    def handle_noargs(self, *args, **kwargs):
        pass

