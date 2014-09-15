import datetime
import random
import json

from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

from cla_provider.serializers import CaseSerializer, EligibilityCheckSerializer, PersonalDetailsSerializer
from cla_provider.models import Provider, ProviderAllocation, OutOfHoursRota
from eligibility_calculator.calculator import EligibilityChecker


class ProviderAllocationHelper(object):

    def __init__(self, as_of=None):
        self._providers_in_category = None
        self.as_of = timezone.localtime(as_of or timezone.now())

    def get_qualifying_providers_allocation(self, category):
        """
        @return: list
        """
        if not self._providers_in_category:
            self._providers_in_category = ProviderAllocation.objects.filter(
                category=category)

        return self._providers_in_category

    def today_at(self, hour, minute=0, second=0, microsecond=0):
        t = timezone.localtime(self.as_of)
        return t.replace(hour=hour, minute=minute, second=second,
                         microsecond=microsecond)

    def get_qualifying_providers(self, category):
        """
        @return: list
        """
        if category:
            return [pa.provider for pa in
                    self.get_qualifying_providers_allocation(category)]

        return Provider.objects.active()

    def _get_random_provider(self, category):
        """
        @return: Randomly chosen provider who offers this category of service
                 or None if there are no providers with this category of
                 service
        """
        def calculate_winner():
            allocations = self.get_qualifying_providers_allocation(category)
            if not allocations:
                return None

            total = sum(pa.weighted_distribution for pa in allocations)

            r = random.uniform(0, total)
            upto = 0
            for pa in allocations:
                if upto + pa.weighted_distribution > r:
                    return pa.provider
                upto += pa.weighted_distribution
            assert False, "Shouldn't get here"
        return calculate_winner()

    def _get_rota_provider(self, category):
        try:
            rota = OutOfHoursRota.objects.get_current(category,
                                                      as_of=self.as_of)
            return rota.provider if rota else None
        except OutOfHoursRota.MultipleObjectsReturned:
            # this should be prevented by OutOfHoursRota.clean but what
            # if something slipped the net. How should it be handled?
            return None
        except OutOfHoursRota.DoesNotExist:
            # if no operator exists then handle it (not yet) but in
            # ticket coming soon #71535438 but there are some blockers
            # (e.g. being able to manually allocate)
            return None

    @property
    def is_bank_holiday(self):
        # TODO: make this work for bank hols
        return False

    @property
    def is_out_of_hours(self):
        weekday = self.as_of.date().weekday()

        # not open on bank holiday
        if self.is_bank_holiday:
            return True

        # if day in MON-FRI (open 09h-17h)
        elif weekday < 5:
            day_start = self.today_at(9)
            day_end = self.today_at(17)
            return not (day_start < self.as_of < day_end)

        # if Saturday (only open in the morning)
        elif weekday == 5:
            day_start = self.today_at(9)
            day_end = self.today_at(12, minute=30)
            return not (day_start < self.as_of < day_end)

        # if Sunday then out of hours (call centre doesn't operate on sunday)
        else:
            return True

    def get_suggested_provider(self, category):
        if self.is_out_of_hours:
            return self._get_rota_provider(category)
        else:
            return self._get_random_provider(category)


def notify_case_assigned(provider, case):
    if not provider.email_address:
        return
    from_address = 'no-reply@digital.justice.gov.uk'
    subject = 'CLA Case {ref} has been assigned to {provider}'.format(**{
        'ref': case.reference,
        'provider': provider.name})
    case_url = 'https://{0}/call_centre/{1}/'
    template_params = {
        'provider': provider,
        'now': datetime.datetime.now(),
        'case_url': case_url.format(settings.SITE_HOSTNAME, case.reference),
        'case': case}
    template = 'cla_provider/email/assigned.{0}'
    text = render_to_string(template.format('txt'), template_params)
    html = render_to_string(template.format('html'), template_params)
    email = EmailMultiAlternatives(
        subject, text, from_address, [provider.email_address])
    email.attach_alternative(html, 'text/html')
    email.send()


class LegalHelpExtract(object):

    def __init__(self, case):
        self.case = case

    def format(self):
        eligibility_check = EligibilityCheckSerializer(instance=self.case.eligibility_check).data
        calculator = EligibilityChecker(self.case.eligibility_check.to_case_data())

        ctx = {
            'case': CaseSerializer(instance=self.case).data,
            'personal_details': PersonalDetailsSerializer(instance=self.case.personal_details).data,
            'eligibility_check': EligibilityCheckSerializer(instance=self.case.eligibility_check).data,
            'calculator': {
              'partner_allowance': calculator.partner_allowance,
              'employment_allowance': calculator.employment_allowance,
              'dependants_allowance': calculator.dependants_allowance,
              'partner_employment_allowance': calculator.partner_employment_allowance,
              'pensioner_disregard': calculator.pensioner_disregard,
              'total_disposable_income': calculator.disposable_income,
              'total_capital': calculator.disposable_capital_assets
            }
        }
        return HttpResponse(json.dumps(ctx, cls=DjangoJSONEncoder), content_type='text/json')
