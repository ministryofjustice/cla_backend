from django.core.management import BaseCommand
from legalaid.models import ContactResearchMethod, PersonalDetails
import uuid
from cla_common.constants import RESEARCH_CONTACT_VIA


class Command(BaseCommand):
    help = "Creates the contact for research methods default entities AND migrates data from contact_for_research_via field"

    def handle(self, *args, **options):
        for (value, label) in RESEARCH_CONTACT_VIA:
            (method, created) = ContactResearchMethod.objects.get_or_create(
                method=value, defaults={"reference": uuid.uuid4()}
            )
            details_qs = PersonalDetails.objects.filter(
                contact_for_research_via=value, contact_for_research_methods__isnull=True
            )
            self.stdout.write(
                "Processing {method}...migrating {count} records from contact_for_research_via field".format(
                    method=value, count=details_qs.count()
                )
            )
            for details in details_qs:
                details.contact_for_research_methods.add(method)
