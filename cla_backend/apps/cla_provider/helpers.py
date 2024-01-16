from collections import defaultdict, OrderedDict
import datetime
import os
import random
from itertools import groupby
from operator import itemgetter

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.conf import settings
from django.db.models import Count

from govuk_notify.api import NotifyEmailOrchestrator
from cla_provider.models import (
    Provider,
    ProviderAllocation,
    OutOfHoursRota,
    ProviderPreAllocation,
    get_current_day_as_string,
)
from legalaid.models import Case
import logging

logger = logging.getLogger()


class ProviderDistributionHelper(object):
    def __init__(self, dt=None):
        self.date = dt.replace(hour=0, minute=0, second=0) if dt else None

    def get_distribution(self, category, include_pre_allocations=False):
        last_update = ProviderAllocation.objects.filter(category=category).order_by("-modified").first()

        raw = (
            Case.objects.order_by("provider")
            .filter(diagnosis__category=category)
            .filter(assigned_out_of_hours=False)
            .exclude(log__code="MANREF")
            .exclude(provider=None)
        )

        if self.date:
            raw = raw.filter(provider_assigned_at__gte=self.date)

        if last_update:
            raw = raw.filter(provider_assigned_at__gte=last_update.modified)

        raw = raw.values("provider").annotate(num_allocations=Count("id"))
        ret = defaultdict(int)
        for item in raw:
            ret[item["provider"]] += item["num_allocations"]

        if include_pre_allocations:
            preallocs = (
                ProviderPreAllocation.objects.order_by("provider")
                .filter(category=category)
                .values("provider")
                .annotate(num_allocations=Count("case"))
            )
            for item in preallocs:
                ret[item["provider"]] += item["num_allocations"]

        return ret

    def make_ideal(self, num_cases, weights):
        """
        :param num_cases: number of cases
        :type num_cases: int
        :param weights: weights for each of the provider
        :type weights: List{ProviderAllocation}
        :return: dict of {provider_id, provider__count}
        similar to the format returned by ProviderDistributionHelper.get_distribution()
        :rtype: dict
        """
        total = sum(pa.weighted_distribution for pa in weights)
        ret = defaultdict(int)
        for pa in weights:
            percent = pa.weighted_distribution / total
            should_have_num_cases = num_cases * percent
            ret[pa.provider.id] = should_have_num_cases

        return ret


class ProviderAllocationHelper(object):
    def __init__(self, as_of=None):
        self._providers_in_category = None
        self.as_of = timezone.localtime(as_of or timezone.now())
        self.distribution = ProviderDistributionHelper()

    def get_qualifying_providers_allocation(self, category):
        """
        @return: list
        """

        if category.code == "education":
            return self.get_valid_education_providers(category)

        if not self._providers_in_category:
            self._providers_in_category = ProviderAllocation.objects.filter(category=category, provider__active=True)

        return self._providers_in_category

    def get_qualifying_providers(self, category):
        """
        @return: list
        """
        if category:
            return [pa.provider for pa in self.get_qualifying_providers_allocation(category)]

        return Provider.objects.active()

    def _get_random_provider(self, category, limit_choices_to=None):
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
            if limit_choices_to:
                allocations = allocations.filter(provider__id__in=limit_choices_to)
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
            rota = OutOfHoursRota.objects.get_current(category, as_of=self.as_of)
            return rota.provider if rota and rota.provider.active else None
        except OutOfHoursRota.MultipleObjectsReturned:
            # this should be prevented by OutOfHoursRota.clean but what
            # if something slipped the net. How should it be handled?
            return None
        except OutOfHoursRota.DoesNotExist:
            # if no operator exists then handle it (not yet) but in
            # ticket coming soon #71535438 but there are some blockers
            # (e.g. being able to manually allocate)
            return None

    def _diff_distributions(self, current_distribution, current_ideal_distribution):
        provider_alloc_diff = {}
        for provider_id, ideal_num_cases in current_ideal_distribution.items():
            provider_alloc_diff[provider_id] = current_distribution[provider_id] - ideal_num_cases
        return provider_alloc_diff

    def _group_dict_by_value(self, provider_alloc_diff):
        groups = OrderedDict()
        data = sorted(provider_alloc_diff.items(), key=itemgetter(1))
        for k, g in groupby(data, itemgetter(1)):
            groups[k] = list(g)
        return groups

    def _get_best_fit_provider(self, category):
        current_distribution = self.distribution.get_distribution(category, include_pre_allocations=True)
        total_current_cases = sum(current_distribution.values())

        # if the number of cases allocated today is zero then just return a random provider
        if total_current_cases == 0:
            return self._get_random_provider(category)

        allocations = self.get_qualifying_providers_allocation(category)

        current_ideal_distribution = self.distribution.make_ideal(total_current_cases, allocations)

        # if the current distribution is already the idea for current number of cases then
        # just pick a random one
        if current_distribution == current_ideal_distribution:
            return self._get_random_provider(category)

        provider_alloc_diff = self._diff_distributions(current_distribution, current_ideal_distribution)

        groups = self._group_dict_by_value(provider_alloc_diff)

        if len(groups) == 1:
            # if everyone has the same score then pick random provider
            return self._get_random_provider(category)
        if len(groups) > 1:
            # there is more than one score take the top one
            first_group = dict(groups.items()[0][1])
            if len(first_group) > 1:
                # if there is more than one provider with the same score,
                # randomly pick one from those with the same score
                return self._get_random_provider(category, limit_choices_to=first_group.keys())
            # if there is only one provider then
            return Provider.objects.get(pk=first_group.keys()[0])

        # else everyone doesn't have any allocation so just pick randomly
        return self._get_random_provider(category)

    def is_provider_under_capacity(self, provider_allocation):
        """Returns True or False depending on if the provider is under
        their allocated capacity for a given category.

        Args:
            provider_allocation (cla_provider.ProviderAllocation): A ProviderAllocation object
        """
        category = provider_allocation.category
        current_distribution = self.distribution.get_distribution(category, include_pre_allocations=True)
        total_current_cases = float(sum(current_distribution.values()))

        if total_current_cases == 0:
            # No providers have yet been assigned a case for this category
            return True

        if provider_allocation.provider.id not in current_distribution.keys():
            # The provider has not yet been assigned a case for this category
            return True

        provider_current_num_cases = float(current_distribution[provider_allocation.provider.id])
        current_allocation = provider_current_num_cases / total_current_cases

        if current_allocation >= provider_allocation.weighted_distribution:
            return False  # They are over their allocated capacity

        return True

    def get_valid_education_providers(self, education_category):
        """Gets a list of education ProviderAllocations that
        1) Are active
        2) Are working today, as based off their WorkingDays model
        3) If it is a Thursday:
            Are under their contracted capacity, as determined by their weighted_distribution

        Args:
            education_category (LegalAid.category): The education LegalAid category

        Returns:
            List: Valid education provider allocations, as determined by the above rules.
        """
        provider_allocations = ProviderAllocation.objects.filter(
            category=education_category, provider__active=True
        ).all()
        logger.log(700, provider_allocations)
        provider_allocations = filter(ProviderAllocation.is_working_today, provider_allocations)
        logger.log(700, provider_allocations)

        if get_current_day_as_string() == "thursday":
            provider_allocations = filter(self.is_provider_under_capacity, provider_allocations)
        logger.log(700, provider_allocations)
        return provider_allocations

    def get_suggested_provider(self, category):
        non_rota_hours = settings.NON_ROTA_OPENING_HOURS[getattr(category, "code")]
        if self.as_of not in non_rota_hours:
            return self._get_rota_provider(category)
        if not os.path.isfile("/tmp/DISABLE_BEST_FIT_PROVIDER"):
            return self._get_best_fit_provider(category)
        return self._get_random_provider(category)


def notify_case_assigned(provider, case):
    if not provider.email_address:
        return
    case_url = "https://{0}/provider/{1}/"
    now = datetime.datetime.now()
    personalisation = {
        "reference": case.reference,
        "provider": provider.name,
        "eligibility_check_category": case.eligibility_check.category.name,
        "is_SPOR": case.outcome_code == "SPOR",
        "time": now.strftime("%H:%M"),
        "date": now.strftime("%D"),
        "case_url": case_url.format(settings.FRONTEND_HOST_NAME, case.reference),
    }
    email = NotifyEmailOrchestrator()
    email.send_email(
        email_address=provider.email_address,
        template_id=settings.GOVUK_NOTIFY_TEMPLATES["PROVIDER_CASE_ASSIGNED"],
        personalisation=personalisation,
    )


def notify_case_RDSPed(provider, case):
    if not provider.email_address:
        return
    case_url = "https://{0}/provider/{1}/"
    now = datetime.datetime.now()
    personalisation = {
        "reference": case.reference,
        "time": now.strftime("%H:%M"),
        "date": now.strftime("%D"),
        "case_url": case_url.format(settings.FRONTEND_HOST_NAME, case.reference),
    }
    email = NotifyEmailOrchestrator()
    email.send_email(
        email_address=provider.email_address,
        template_id=settings.GOVUK_NOTIFY_TEMPLATES["PROVIDER_CASE_RDSP"],
        personalisation=personalisation,
    )


class ProviderExtractFormatter(object):
    def __init__(self, case):
        self.case = case

    def format(self):
        ctx = {"case": self.case}
        template = get_template("provider/case.xml")
        resp = HttpResponse(template.render(ctx), content_type="text/xml")
        resp["Access-Control-Allow-Origin"] = "*"
        return resp
