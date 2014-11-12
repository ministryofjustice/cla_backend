import datetime
import random

from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from django.conf import settings

from legalaid.utils.dates import is_out_of_hours_for_providers

from cla_provider.models import Provider, ProviderAllocation, OutOfHoursRota


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

        PLEASE NOTE:
            This can be improved quite a lot (and it should be).

            Only 2 changes are required:

            a/ at each iteration, the algorithm should correct itself by
                getting the current computed allocations and add a +/- boost
                to the allocations for the next iteration

            b/ in order to support changes in allocations, the algorithm should
                only consider the computed allocations after the last modified
                field of the all provider allocations combined only.
                In this way, we would ignore the state before the allocation
                changed.
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

    def get_suggested_provider(self, category):
        if is_out_of_hours_for_providers(self.as_of):
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
    case_url = 'https://{0}/provider/{1}/'
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


class ProviderExtractFormatter(object):
    def __init__(self, case):
        self.case = case

    def format(self):
        ctx = {}
        ctx['case'] = self.case
        template = get_template('provider/case.xml')
        resp = HttpResponse(template.render(Context(ctx)),
                            content_type='text/xml')
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
