import datetime
import json
import types

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings

from .cfe_civil.age import translate_age
from .cfe_civil.deductions import translate_deductions
from .cfe_civil.dependants import translate_dependants
from .cfe_civil.savings import translate_savings
from .cfe_civil.employment import translate_employment
from .cfe_civil.cfe_response import CfeResponse
from .cfe_civil.property import translate_property
from .cfe_civil.income import translate_income
from .cfe_civil.applicant import translate_applicant
from .cfe_civil.under_18_passported import translate_under_18_passported
from .cfe_civil.proceeding_types import translate_proceeding_types, DEFAULT_PROCEEDING_TYPE
from cla_common.constants import ELIGIBILITY_STATES

logger = __import__("logging").getLogger(__name__)


class EligibilityChecker(object):
    def __init__(self, case_data, calcs=None):
        super(EligibilityChecker, self).__init__()
        self.case_data = case_data
        self.calcs = calcs or {}

    def is_eligible(self):
        is_eligible, _, _, _ = self.is_eligible_with_reasons()
        return is_eligible

    def is_eligible_with_reasons(self):
        cfe_result, cfe_calcs, cfe_response = self._do_cfe_civil_check()

        # Calcs updated from CFE's result
        self.calcs = cfe_calcs

        logger.info("Eligibility result (using CFE): %s", cfe_result)

        if cfe_response:
            return (
                cfe_result,
                cfe_response.is_gross_eligible,
                cfe_response.is_disposable_eligible,
                cfe_response.is_capital_eligible,
            )
        else:
            return cfe_result, None, None, None

    @staticmethod
    def _pounds_to_pence(value):
        # deal with rounding error by adding a small amount before truncating
        return int(value * 100 + 0.1)

    @staticmethod
    def _under_18_passported(case_data):
        return (hasattr(case_data.facts, "under_18_passported") and case_data.facts.under_18_passported) and (
            hasattr(case_data.facts, "is_you_under_18") and case_data.facts.is_you_under_18
        )

    @staticmethod
    def _is_non_means_tested(case_data):
        return case_data.facts.on_nass_benefits and case_data.category == "immigration"

    def _do_cfe_civil_check(self):
        # This property is not used by clients, but we support it while it's in the API.
        # CFE doesn't know how to handle this scenario, so just code it here.
        if self.case_data.facts.has_passported_proceedings_letter:
            return ELIGIBILITY_STATES.YES, None, None

        if not EligibilityChecker._is_data_complete_enough_to_call_cfe(self.case_data):
            # data is so incomplete that we can't even call CFE sensibly
            result = ELIGIBILITY_STATES.UNKNOWN
            logger.info("Eligibility result (CFE): %s %s" % (result, "couldn't call CFE"))
            return result, None, None

        cfe_request_dict = self._translate_case(self.case_data)

        user_agent = "cla_backend/1 (%s)" % settings.CLA_ENV
        cfe_raw_response = requests.post(settings.CFE_URL, json=cfe_request_dict, headers={"User-Agent": user_agent})
        logger.debug("Eligibility request (CFE): %s" % json.dumps(cfe_request_dict, indent=4, sort_keys=True))

        cfe_response = CfeResponse(cfe_raw_response.json())
        result, calcs = self._translate_response(cfe_response)
        logger.debug("Eligibility result (CFE): %s" % (json.dumps(cfe_response._cfe_data, indent=4, sort_keys=True)))

        return result, calcs, cfe_response

    @staticmethod
    def _is_data_complete_enough_to_call_cfe(case_data):
        if EligibilityChecker._under_18_passported(case_data):
            # no more info needed
            return True
        if (case_data.facts.on_passported_benefits is None) or (
            case_data.facts.dependants_young is None and not case_data.facts.on_passported_benefits
        ):
            # the gross income threshold may increase, depending on the number of child dependants,
            # so we can't do gross income section - even if we tell CFE it is incomplete, if the gross income
            # is over the threshold it will give 'ineligible'.
            # Therefore to run CFE, we need to know dependants_young, or if they are passported (because the
            # gross income check doesn't come into play)
            logger.info(
                "Eligibility check: CFE can't be called because dependants_young not known (and not passported)"
            )
            return False
        return True

    @staticmethod
    def _translate_case(case_data, submission_date=None):
        """Translates CLA's CaseData to CFE-Civil request JSON"""
        if not submission_date:
            submission_date = datetime.date.today()
        request_data = {
            "assessment": {
                "submission_date": str(submission_date),
                "level_of_help": "controlled",  # CLA is for 'advice' only, so always controlled
            },
            "proceeding_types": [DEFAULT_PROCEEDING_TYPE],
        }

        EligibilityChecker._translate_section_gross_income(case_data, request_data)
        EligibilityChecker._translate_section_disposable_income(case_data, request_data)
        EligibilityChecker._translate_section_capital(case_data, request_data)

        if hasattr(case_data, "category"):
            request_data["proceeding_types"] = translate_proceeding_types(case_data.category)
        if hasattr(case_data, "facts"):
            request_data["applicant"] = EligibilityChecker._translate_applicant_data(submission_date, case_data.facts)
            request_data["assessment"].update(translate_under_18_passported(case_data.facts))
            request_data.update(translate_dependants(submission_date, case_data.facts))
            if hasattr(case_data, "partner") and case_data.facts.should_aggregate_partner:
                request_data["partner"] = EligibilityChecker._translate_partner_data(
                    case_data.partner, submission_date
                )

        request_data.update(EligibilityChecker._translate_capital_data(case_data))

        if hasattr(case_data, "you"):
            request_data.update(EligibilityChecker._translate_income_data(case_data.you))

        return request_data

    @staticmethod
    def _translate_section_gross_income(case_data, request_data):
        def is_income_complete(income):
            income_keys_if_complete = set(income.PROPERTY_META.keys())
            # cla_public will remove the `income.child_benefits` key from CaseDict if you submit /benefits without
            # checking the child benefit checkbox (which doesn't even appear if dependants_young=0). So this key is not
            # required for income to be considered complete
            income_keys_if_complete.remove("child_benefits")
            for key in income_keys_if_complete:
                if getattr(income, key) is None:
                    return False
            return True

        """
        Determine if the questions for gross income section of the test have been completed by the user yet,
        and put this in the CFE request.
        """

        def is_gross_income_complete(case_data):
            if not is_income_complete(case_data.you.income):
                return False

            if case_data.facts.has_partner and not is_income_complete(case_data.partner.income):
                # If they have a partner then their deductions can lower the disposable income further,
                # so this section is not complete until we know the partners' figures
                return False

            return True

        if not is_gross_income_complete(case_data):
            request_data["assessment"]["section_gross_income"] = "incomplete"

    @staticmethod
    def _translate_section_disposable_income(case_data, request_data):
        """
        Determine if the questions for disposable income section of the test have been completed by the user yet,
        and put this in the CFE request.
        """

        def is_disposable_income_complete(case_data):
            if not is_deductions_complete(case_data.you.deductions):
                return False

            if case_data.facts.has_partner and not is_deductions_complete(case_data.partner.deductions):
                # If they have a partner then their deductions can lower the disposable income further,
                # so this section is not complete until we know the partners' figures
                return False
            return True

        if not is_disposable_income_complete(case_data):
            request_data["assessment"]["section_disposable_income"] = "incomplete"

    @staticmethod
    def is_property_complete(case_data):
        if not hasattr(case_data.facts, "has_partner"):
            # If they have a partner then that may increase assets that they need to delare, so
            # this section is not complete until we clear up if there is a partner
            return False

        if len(case_data.property_data) == 0:
            return True
        for key, value in case_data.property_data[0].iteritems():
            if value is not None:
                return True
        return False

    @staticmethod
    def _is_savings_complete(case_data):
        def is_savings_data_complete(savings):
            for key in savings.PROPERTY_META:
                if not isinstance(getattr(savings, key), (types.IntType, types.LongType)):
                    return False
            return True

        if case_data.facts.has_partner:
            # If they have a partner then that may increase assets that they need to delare, so
            # this section is not complete until we clear up if there is a partner
            if not is_savings_data_complete(case_data.partner.savings):
                return False
        return is_savings_data_complete(case_data.you.savings)

    @staticmethod
    def _translate_section_capital(case_data, request_data):
        """
        Determine if the questions for capital section of the test have been completed by the user yet,
        and put this in the CFE request.
        """
        has_completed_capital_questions = EligibilityChecker.is_property_complete(
            case_data
        ) and EligibilityChecker._is_savings_complete(case_data)

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
            request_data["assessment"]["section_capital"] = "incomplete"

    @staticmethod
    def _translate_partner_data(partner, submission_date):
        # default DOB to 'nothing special' 40 years old rules-wise
        # as all we have is you/partner over 60 - so we don't know or care
        # how old the partner is
        partner_dob = str(submission_date - relativedelta(years=40))
        request_data = {"partner": {"date_of_birth": partner_dob}}
        request_data.update(translate_savings(partner.savings))

        request_data.update(EligibilityChecker._translate_income_data(partner))

        return request_data

    @staticmethod
    def _translate_income_data(person):
        request_data = {}
        regular_income = translate_income(person.income)
        request_data.update(translate_employment(person.income, person.deductions))
        regular_outgoings = translate_deductions(person.deductions)
        request_data.update(EligibilityChecker._merge_regular_transaction_data(regular_income, regular_outgoings))

        return request_data

    @staticmethod
    def _merge_regular_transaction_data(regular_income, regular_outgoings):
        if "regular_transactions" in regular_outgoings:
            if "regular_transactions" in regular_income:
                return dict(
                    regular_transactions=regular_income["regular_transactions"]
                    + regular_outgoings["regular_transactions"]
                )
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
        request_data.update(translate_savings(case_data.you.savings))
        request_data.update(translate_property(case_data.property_data))

        disputed_savings = translate_savings(case_data.disputed_savings, subject_matter_of_dispute=True)
        capitals = request_data["capitals"]
        disputed_capitals = disputed_savings["capitals"]
        for key in capitals.keys():
            capitals[key] += disputed_capitals[key]
        return request_data

    def _translate_response(self, cfe_response):
        """Translates CFE-Civil's response to ELIGIBILITY_STATES and calcs"""
        if cfe_response.overall_result in ("eligible", "contribution_required"):
            result = ELIGIBILITY_STATES.YES
        elif cfe_response.overall_result == "ineligible":
            result = ELIGIBILITY_STATES.NO
        elif cfe_response.overall_result == "not_yet_known":
            result = ELIGIBILITY_STATES.UNKNOWN
        else:
            logger.error("cfe_response.overall_result not recognised: %s" % cfe_response.overall_result)

        calcs = {
            "pensioner_disregard": self._pounds_to_pence(cfe_response.pensioner_disregard),
            "disposable_capital_assets": self._pounds_to_pence(cfe_response.disposable_capital_assets),
            "property_equities": [self._pounds_to_pence(x) for x in cfe_response.property_equities],
            "property_capital": self._pounds_to_pence(cfe_response.property_capital),
            "non_property_capital": self._pounds_to_pence(
                cfe_response.liquid_capital + cfe_response.non_liquid_capital + cfe_response.vehicle_capital
            ),
            "gross_income": self._pounds_to_pence(cfe_response.gross_income),
            "partner_allowance": self._pounds_to_pence(cfe_response.partner_allowance),
            "disposable_income": self._pounds_to_pence(cfe_response.disposable_income),
            "dependants_allowance": self._pounds_to_pence(cfe_response.dependants_allowance),
            "employment_allowance": self._pounds_to_pence(cfe_response.employment_allowance),
            "partner_employment_allowance": 0,
        }
        return result, calcs

    def should_passport_nass(self):
        return self.case_data.category and self.case_data.category == "immigration"
