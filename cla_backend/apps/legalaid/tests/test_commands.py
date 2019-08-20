from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
from core.tests.mommy_utils import make_recipe, make_user
from legalaid.models import Case


class CaseOrganisationAssignmentTestCase(TestCase):
    def test_assign_existing_cases_to_organisation(self):
        agilisys_org = make_recipe("call_centre.organisation", name="Agilisys")
        foo_org = make_recipe("call_centre.organisation", name="Foo org")

        agilisys_operator = make_recipe("call_centre.operator", user=make_user(email="user1@agilisys.co.uk"))
        agilisys_case = make_recipe("legalaid.case", created_by=agilisys_operator.user)
        foo_org_case = make_recipe("legalaid.case", organisation=foo_org)
        no_org_case = make_recipe("legalaid.case")

        out = StringIO()
        call_command("assign_existing_cases_to_organisation", stdout=out)
        self.assertIn("2 cases found.", out.getvalue())

        # Rerun command should result in no changes
        call_command("assign_existing_cases_to_organisation", stdout=out)
        self.assertIn("0 cases found.", out.getvalue())

        # Cases without organisation should have their organisation set to Agilisys
        case_reloaded = Case.objects.get(pk=no_org_case.id)
        self.assertIsNotNone(case_reloaded.organisation)
        self.assertEqual(case_reloaded.organisation.id, agilisys_org.id)

        # Cases belonging to operators with an organisation should have case organisation
        # set to that operators organisation
        case_reloaded = Case.objects.get(pk=agilisys_case.id)
        self.assertIsNotNone(case_reloaded.organisation)
        self.assertEqual(case_reloaded.organisation.id, agilisys_org.id)

        # Cases already belonging to an organisation should not have their organisation changed
        case_reloaded = Case.objects.get(pk=foo_org_case.id)
        self.assertIsNotNone(case_reloaded.organisation)
        self.assertEqual(case_reloaded.organisation.id, foo_org_case.organisation.id)
