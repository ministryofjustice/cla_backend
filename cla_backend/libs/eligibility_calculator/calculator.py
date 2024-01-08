import datetime
import json
import types

import requests
from django.conf import settings
from django.utils import timezone

from . import constants
from . import exceptions
from .cfe_civil.age import translate_age
from .cfe_civil.deductions import translate_deductions
from .cfe_civil.dependants import translate_dependants
from .cfe_civil.savings import translate_savings
from .cfe_civil.employment import translate_employment
from .cfe_civil.cfe_response import CfeResponse
from .cfe_civil.property import translate_property
from .cfe_civil.income import translate_income
from .cfe_civil.applicant import translate_applicant
from .cfe_civil.proceeding_types import translate_proceeding_types, DEFAULT_PROCEEDING_TYPE
from cla_common.constants import ELIGIBILITY_STATES

logger = __import__("logging").getLogger(__name__)


class cached_calcs_property(object):
    def __init__(self, func):
        self.func = func

    def _do_get(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res

    def __get__(self, instance, type=None):
        res = self._do_get(instance, type)
        if "calcs" not in instance.__dict__:
            instance.__dict__["calcs"] = {}
        instance.__dict__["calcs"][self.func.__name__] = res
        return res


class CapitalCalculator(object):
    def __init__(self, properties=[], non_disputed_liquid_capital=0, disputed_liquid_capital=0, calcs={}):
        self.properties = self._parse_props(properties)
        self.non_disputed_liquid_capital = non_disputed_liquid_capital
        self.disputed_liquid_capital = disputed_liquid_capital
        self.calcs = calcs

    def _parse_props(self, props):
        result = []
        for p in props or []:
            # check property
            invalid_props, is_empty = self._is_property_invalid(p)
            if invalid_props:
                if not is_empty:
                    raise exceptions.PropertyExpectedException(
                        "'Property' requires attribute '{kw}' and was not given at __init__".format(kw=invalid_props)
                    )
                continue

            parsed_prop = p.copy()
            parsed_prop["equity"] = 0
            result.append(parsed_prop)
        return result

    @property
    def main_property(self):
        if not hasattr(self, "_main_property"):
            self._main_property = None
            if self.properties:
                for prop in self.properties:
                    if prop["main"]:
                        self._main_property = prop
                        break
        return self._main_property

    @property
    def other_properties(self):
        if not hasattr(self, "_other_properties"):
            self._other_properties = []
            if self.properties:
                self._other_properties = [prop for prop in self.properties if not prop["main"]]
        return self._other_properties

    def _is_property_invalid(self, prop):
        """
        Returns tuple (<is-invalid>, <is-empty>) where:
            is-invalid: is a list of invalid (none-values) keys
            is-empty: True if all the values are None
        """
        if not prop:
            return (True, True)

        none_values = [k for k, v in prop.items() if v is None]
        return none_values, len(none_values) == len(prop)

    @staticmethod
    def is_post_mortgage_cap_removal():
        if not hasattr(settings, "MORTGAGE_CAP_REMOVAL_DATE"):
            return False

        dt = timezone.make_aware(settings.MORTGAGE_CAP_REMOVAL_DATE, timezone.get_current_timezone())
        return timezone.now() >= dt

    # for each other property
    def _calculate_property_equity(self, prop):
        if not prop:
            return

        def pre_mortgage_cap_removal():
            mortgage_disregard = min(prop["mortgage_left"], self.mortgage_disregard_available)

            property_equity = prop["value"] - mortgage_disregard
            # if prop.in_joint_names:
            property_equity = (
                property_equity * prop["share"] / 100
            )  # assuming that you filled in share with the right figure (that is, in_joint_names not required)

            remaining_mortgage_disregard = self.mortgage_disregard_available - mortgage_disregard

            prop["equity"] = max(property_equity, 0)
            self.mortgage_disregard_available = remaining_mortgage_disregard

        def post_mortgage_cap_removal():
            mortgage_disregard = prop["mortgage_left"]

            property_equity = prop["value"] - mortgage_disregard
            # if prop.in_joint_names:
            property_equity = (
                property_equity * prop["share"] / 100
            )  # assuming that you filled in share with the right figure (that is, in_joint_names not required)

            prop["equity"] = max(property_equity, 0)

        if self.is_post_mortgage_cap_removal():
            post_mortgage_cap_removal()
        else:
            pre_mortgage_cap_removal()

    def _apply_SMOD_disregard(self, prop):
        if not prop or not prop["disputed"]:
            return

        SMOD_disregard = min(prop["equity"], self.SMOD_disregard_available)

        prop["equity"] = max(prop["equity"] - SMOD_disregard, 0)
        remaining_SMOD_disregard = self.SMOD_disregard_available - SMOD_disregard

        self.SMOD_disregard_available = remaining_SMOD_disregard

    def _apply_equity_disregard(self, prop):
        if not prop:
            return
        # if not prop.disputed:
        #     return

        prop["equity"] = max(prop["equity"] - self.equity_disregard_available, 0)

    def _reset_state(self):
        self.mortgage_disregard_available = constants.MORTGAGE_DISREGARD
        self.SMOD_disregard_available = constants.SMOD_DISREGARD
        self.equity_disregard_available = constants.EQUITY_DISREGARD

        for prop in self.properties:
            prop["equity"] = 0

    @cached_calcs_property
    def property_capital(self):
        if not self.properties:
            return 0

        # calculating equities
        for other_property in self.other_properties:
            self._calculate_property_equity(other_property)

        self._calculate_property_equity(self.main_property)

        # applying SMOD disregard
        self._apply_SMOD_disregard(self.main_property)

        for other_property in self.other_properties:
            self._apply_SMOD_disregard(other_property)

        # applying equity disregard (to main home only)
        self._apply_equity_disregard(self.main_property)

        property_capital = 0
        for prop in self.properties:
            property_capital += prop["equity"]
        return property_capital

    @cached_calcs_property
    def liquid_capital(self):
        SMOD_disregard = min(self.disputed_liquid_capital, self.SMOD_disregard_available)

        capital = max(self.disputed_liquid_capital - SMOD_disregard, 0)

        capital += self.non_disputed_liquid_capital

        return capital

    def calculate_capital(self):
        self._reset_state()

        res = self.property_capital + self.liquid_capital

        self.calcs["property_equities"] = [prop.get("equity", 0) for prop in self.properties]

        return res


class EligibilityChecker(object):
    def __init__(self, case_data, calcs=None):
        super(EligibilityChecker, self).__init__()
        self.case_data = case_data
        self.calcs = calcs or {}

    @cached_calcs_property
    def gross_income(self):
        return self.case_data.total_income

    @cached_calcs_property
    def partner_allowance(self):
        if self.case_data.facts.has_partner:
            return constants.PARTNER_ALLOWANCE
        return 0

    @cached_calcs_property
    def employment_allowance(self):
        if self.case_data.you.income.has_employment_earnings and not self.case_data.you.income.self_employed:
            return constants.EMPLOYMENT_COSTS_ALLOWANCE
        return 0

    @cached_calcs_property
    def partner_employment_allowance(self):
        if self.case_data.facts.has_partner and self.case_data.facts.should_aggregate_partner:
            if (
                self.case_data.partner.income.has_employment_earnings
                and not self.case_data.partner.income.self_employed
            ):
                return constants.EMPLOYMENT_COSTS_ALLOWANCE
            return 0
        return 0

    @cached_calcs_property
    def dependants_allowance(self):
        return self.case_data.facts.dependant_children * constants.CHILD_ALLOWANCE

    @cached_calcs_property
    def pensioner_disregard(self):
        if self.case_data.facts.is_you_or_your_partner_over_60:
            return constants.PENSIONER_DISREGARD_LIMIT_LEVELS.get(max(self.disposable_income, 0), 0)
        return 0

    @cached_calcs_property
    def disposable_income(self):
        if not hasattr(self, "_disposable_income"):
            gross_income = self.gross_income

            gross_income -= self.partner_allowance

            # children
            gross_income -= self.dependants_allowance

            # Tax + NI
            income_tax_and_ni = (
                self.case_data.you.deductions.income_tax + self.case_data.you.deductions.national_insurance
            )
            gross_income -= income_tax_and_ni
            if self.case_data.facts.should_aggregate_partner:
                income_tax_and_ni = (
                    self.case_data.partner.deductions.income_tax + self.case_data.partner.deductions.national_insurance
                )
                gross_income -= income_tax_and_ni

            # maintenance 6.3
            gross_income -= self.case_data.you.deductions.maintenance
            if self.case_data.facts.should_aggregate_partner:
                gross_income -= self.case_data.partner.deductions.maintenance

            # housing
            mortgage_or_rent = self.case_data.you.deductions.mortgage  # excl housing benefit
            mortgage_or_rent += self.case_data.you.deductions.rent
            if self.case_data.facts.should_aggregate_partner:
                mortgage_or_rent += self.case_data.partner.deductions.mortgage
                mortgage_or_rent += self.case_data.partner.deductions.rent

            if not self.case_data.facts.dependant_children and not self.case_data.facts.has_partner:
                mortgage_or_rent = min(mortgage_or_rent, constants.CHILDLESS_HOUSING_CAP)
            gross_income -= mortgage_or_rent

            # employment allowance
            gross_income -= self.employment_allowance
            gross_income -= self.partner_employment_allowance

            # criminal
            gross_income -= self.case_data.you.deductions.criminal_legalaid_contributions  # not for now
            if self.case_data.facts.should_aggregate_partner:
                gross_income -= self.case_data.partner.deductions.criminal_legalaid_contributions

            # childcare 6.5.2
            gross_income -= self.case_data.you.deductions.childcare
            if self.case_data.facts.should_aggregate_partner:
                gross_income -= self.case_data.partner.deductions.childcare

            self._disposable_income = gross_income

        return self._disposable_income

    @cached_calcs_property
    def disposable_capital_assets(self):
        if not hasattr(self, "_disposable_capital_assets"):
            # NOTE: problem in case of disputed partner (and joined savings/assets)

            capital_calc = CapitalCalculator(
                properties=self.case_data.property_data,
                non_disputed_liquid_capital=self.case_data.non_disputed_liquid_capital,
                disputed_liquid_capital=self.case_data.disputed_liquid_capital,
                calcs=self.calcs,
            )
            disposable_capital = capital_calc.calculate_capital()

            disposable_capital -= self.pensioner_disregard

            disposable_capital = max(disposable_capital, 0)

            self._disposable_capital_assets = disposable_capital

        return self._disposable_capital_assets

    def is_gross_income_eligible(self):
        if self.case_data.facts.on_passported_benefits:
            return True

        limit = constants.get_gross_income_limit(self.case_data.facts.dependant_children)
        return self.gross_income <= limit

    def is_disposable_income_eligible(self):
        if self.case_data.facts.on_passported_benefits:
            return True

        return self.disposable_income <= constants.LIMIT

    def is_disposable_capital_eligible(self):
        limit = constants.get_disposable_capital_limit(self.case_data.category)
        return self.disposable_capital_assets <= limit

    def is_eligible(self):
        cfe_result, cfe_calcs, cfe_response = self._do_cfe_civil_check()
        legacy_result = self._legacy_check()
        logger.info("Eligibility result (legacy): %s %s" % (legacy_result, self.calcs))

        # Gradual cut-over from using legacy_result to cfe_result
        if self._is_non_means_tested(self.case_data) or self._without_partner(self.case_data):

            # Calcs updated from CFE's result
            self.calcs = cfe_calcs

            return cfe_result
        else:
            return legacy_result

    @staticmethod
    def _pounds_to_pence(value):
        # deal with rounding error by adding a small amount before truncating
        return int(value * 100 + 0.1)

    @staticmethod
    def _without_partner(case_data):
        return hasattr(case_data.facts, "has_partner") and not case_data.facts.has_partner

    @staticmethod
    def _is_non_means_tested(case_data):
        return case_data.facts.on_nass_benefits and case_data.category == "immigration"

    def _do_cfe_civil_check(self):
        if not EligibilityChecker._is_applicant_detail_section_complete(self.case_data):
            # data is so incomplete that we can't even call CFE sensibly
            result = ELIGIBILITY_STATES.UNKNOWN
            logger.info("Eligibility result (CFE): %s %s" % (result, "couldnt call CFE"))
            return result, None, None

        cfe_request_dict = self._translate_case(self.case_data)

        cfe_raw_response = requests.post(settings.CFE_URL, json=cfe_request_dict)
        logger.debug("Eligibility request (CFE): %s" % json.dumps(cfe_request_dict, indent=4, sort_keys=True))

        cfe_response = CfeResponse(cfe_raw_response.json())
        result, calcs = self._translate_response(cfe_response)
        logger.info("Eligibility result (CFE): %s %s" % (result, cfe_response.overall_result))
        logger.debug(
            "Eligibility result (CFE): %s" % (json.dumps(cfe_response._cfe_data, indent=4, sort_keys=True)))

        return result, calcs, cfe_response

    @staticmethod
    def _is_applicant_detail_section_complete(case_data):
        return hasattr(case_data.facts, "dependants_young") and hasattr(case_data.facts, "has_partner")

    @staticmethod
    def _translate_case(case_data, submission_date=None):
        '''Translates CLA's CaseData to CFE-Civil request JSON'''
        if not submission_date:
            submission_date = datetime.date.today()
        # produce the simplest possible plain request to CFE to prove the route
        request_data = {
            "assessment": {
                "submission_date": str(submission_date),
                "level_of_help": "controlled"  # CLA is for 'advice' only, so always controlled
            },
            "applicant": {
                "date_of_birth": "1992-07-25",
                "receives_qualifying_benefit": False,
                "receives_asylum_support": False,
            },
            "proceeding_types": [
                DEFAULT_PROCEEDING_TYPE
            ]
        }

        EligibilityChecker._translate_section_gross_income(case_data, request_data)
        EligibilityChecker._translate_section_disposable_income(case_data, request_data)
        EligibilityChecker._translate_section_capital(case_data, request_data)
        if hasattr(case_data, "category"):
            request_data["proceeding_types"] = translate_proceeding_types(case_data.category)
        if hasattr(case_data, "facts"):
            request_data['applicant'].update(
                EligibilityChecker._translate_applicant_data(submission_date, case_data.facts))
            request_data.update(translate_dependants(submission_date, case_data.facts))

        request_data.update(EligibilityChecker._translate_capital_data(case_data))

        if hasattr(case_data, "you"):
            request_data.update(EligibilityChecker._translate_income_data(case_data.you))

        return request_data

    @staticmethod
    def _translate_section_gross_income(case_data, request_data):
        """
        Determine if the questions for gross income section of the test have been completed by the user yet,
        and put this in the CFE request.
        """
        def is_gross_income_complete(case_data):
            if not hasattr(case_data, "you"):
                return False
            person = case_data.you
            if not hasattr(person, "income"):
                return False
            income = person.income
            for key in income.PROPERTY_META:
                if not hasattr(income, key):
                    return False
            return True

        if not is_gross_income_complete(case_data):
            request_data['assessment']['section_gross_income'] = 'incomplete'

    @staticmethod
    def _translate_section_disposable_income(case_data, request_data):
        """
        Determine if the questions for disposable income section of the test have been completed by the user yet,
        and put this in the CFE request.
        """
        def is_disposable_income_complete(case_data):
            if not hasattr(case_data, "you"):
                return False
            person = case_data.you
            if not hasattr(person, "deductions"):
                return False
            deductions = case_data.you.deductions
            for key in deductions.PROPERTY_META:
                if not hasattr(deductions, key):
                    return False
            return True

        if not is_disposable_income_complete(case_data):
            request_data['assessment']['section_disposable_income'] = 'incomplete'

    @staticmethod
    def is_property_complete(property_data):
        if len(property_data) == 0:
            return True
        for key, value in property_data[0].iteritems():
            if value is not None:
                return True
        return False

    @staticmethod
    def is_savings_complete(case_data):
        try:
            savings = case_data.you.savings
            for key in savings.PROPERTY_META:
                if not isinstance(getattr(savings, key), (types.IntType, types.LongType)):
                    return False
        except exceptions.PropertyExpectedException:
            return False
        return True

    @staticmethod
    def _translate_section_capital(case_data, request_data):
        """
        Determine if the questions for capital section of the test have been completed by the user yet,
        and put this in the CFE request.
        """
        has_completed_capital_questions = (
            EligibilityChecker.is_property_complete(case_data.property_data)
            and EligibilityChecker.is_savings_complete(case_data)
        )

        # This capital logic is a bit complicated, and dependent on how cla_backend's clients set the CaseData.
        # If we wanted to simplify this logic, here are the concerns:
        # 1. At the start of the flow, `section_capital` can be anything, because we rely on the fact that
        #    `section_disposable_income = incomplete` to force CFE to give `overall_result: not_yet_known`
        # 2. At the end of the capital section of the form, if the total capital is over the threshold, we need CFE
        #    to give `overall_result: ineligible`, causing the front-end to skip to the end of the questions. This
        #    happens whether we tell CFE that `section_capital` is complete or not, so again it doesn't matter.
        # 3. At the time the forms are complete - all the relevant questions have been asked - then we need
        #    `section_capital = complete`, otherwise CFE will give `overall_result: not_yet_known` instead of
        #    `eligible`.
        # So the really simple way to do this is to always set `section_capital = complete`, but that might confuse
        # a dev who looks at the CFE requests before the capital section is in reality complete.
        if not has_completed_capital_questions:
            request_data['assessment']['section_capital'] = 'incomplete'

    @staticmethod
    def _translate_income_data(person):
        request_data = {}
        if hasattr(person, "income"):
            regular_income = translate_income(person.income)
            if hasattr(person, "deductions"):
                request_data.update(translate_employment(person.income, person.deductions))
                regular_outgoings = translate_deductions(person.deductions)
                request_data.update(
                    EligibilityChecker._merge_regular_transaction_data(regular_income, regular_outgoings))
            else:
                request_data.update(regular_income)

        return request_data

    @staticmethod
    def _merge_regular_transaction_data(regular_income, regular_outgoings):
        if "regular_transactions" in regular_outgoings:
            if "regular_transactions" in regular_income:
                return dict(regular_transactions=regular_income["regular_transactions"] + regular_outgoings[
                    "regular_transactions"])
            else:
                return regular_outgoings
        else:
            return regular_income

    @staticmethod
    def _translate_applicant_data(submission_date, facts):
        request_data = {}
        request_data.update(translate_age(submission_date, facts))
        request_data.update(translate_applicant(facts))

        return request_data

    @staticmethod
    def _translate_capital_data(case_data):
        request_data = {}
        if hasattr(case_data, "you") and hasattr(case_data.you, "savings"):
            request_data.update(translate_savings(case_data.you.savings))

        if hasattr(case_data, "property_data"):
            request_data.update(translate_property(case_data.property_data))

        if hasattr(case_data, "disputed_savings"):
            request_data.update(translate_savings(case_data.disputed_savings, subject_matter_of_dispute=True))
        return request_data

    def _translate_response(self, cfe_response):
        '''Translates CFE-Civil's response to ELIGIBILITY_STATES and calcs'''
        if cfe_response.overall_result in ('eligible', 'contribution_required'):
            result = ELIGIBILITY_STATES.YES
        elif cfe_response.overall_result == 'ineligible':
            result = ELIGIBILITY_STATES.NO
        elif cfe_response.overall_result == 'not_yet_known':
            result = ELIGIBILITY_STATES.UNKNOWN
        else:
            logger.error('cfe_response.overall_result not recognised: %s' % cfe_response.overall_result)

        calcs = {
            "pensioner_disregard": self._pounds_to_pence(cfe_response.pensioner_disregard),
            "disposable_capital_assets": self._pounds_to_pence(cfe_response.disposable_capital_assets),
            "property_equities": [self._pounds_to_pence(x) for x in cfe_response.property_equities],
            "property_capital": self._pounds_to_pence(cfe_response.property_capital),
            "liquid_capital": self._pounds_to_pence(cfe_response.liquid_capital + cfe_response.non_liquid_capital + cfe_response.vehicle_capital),
            "gross_income": self._pounds_to_pence(cfe_response.gross_income),
            "partner_allowance": 0,
            "disposable_income": self._pounds_to_pence(cfe_response.disposable_income),
            "dependants_allowance": 0,
            "employment_allowance": self._pounds_to_pence(cfe_response.employment_allowance),
            "partner_employment_allowance": 0,
        }
        return result, calcs

    def _legacy_check(self):
        try:

            if self.case_data.facts.has_passported_proceedings_letter:
                return ELIGIBILITY_STATES.YES

            if self.case_data.facts.under_18_passported:
                return ELIGIBILITY_STATES.YES

            if self.case_data.facts.on_nass_benefits and self.should_passport_nass():
                return ELIGIBILITY_STATES.YES

            if not self.is_disposable_capital_eligible():
                return ELIGIBILITY_STATES.NO

            if not self.is_gross_income_eligible():
                return ELIGIBILITY_STATES.NO

            if not self.is_disposable_income_eligible():
                return ELIGIBILITY_STATES.NO

            return ELIGIBILITY_STATES.YES

        except exceptions.PropertyExpectedException as exc:
            # e.g. 'Facts' requires attribute 'has_partner'
            # This occurs when there's not enough info in self.case_data to give a definitive calculation result
            logger.info("Eligibility result (legacy) unknown: %s %s" % (exc.__class__.__name__, exc))
            return ELIGIBILITY_STATES.UNKNOWN

    def should_passport_nass(self):
        return self.case_data.category and self.case_data.category == "immigration"
