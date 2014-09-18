from decimal import Decimal, InvalidOperation
import json
import re

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from eligibility_calculator.calculator import EligibilityChecker
from eligibility_calculator.models import CaseData


@api_view(['POST'])
@permission_classes((AllowAny,))
def eligibility_batch_check(request):
    return Response(map(pass_fail, request.DATA))


def pass_fail(scenario):
    case_data = CaseData(**to_case_data(scenario))
    scenario = EligibilityChecker(case_data)
    return 'P' if scenario.is_eligible() else 'F'


def to_case_data(scenario):
    benefits = scenario['benefits'].split(',')
    benefits = map(slugify, benefits)

    case = {}
    case['category'] = scenario['law-area'].lower()
    case['property_data'] = properties(scenario)
    case['facts'] = {
        'dependants_old': number(scenario['over16']),
        'dependants_young': number(scenario['under16']),
        'has_partner': is_yes(scenario['partner']),
        'is_you_or_your_partner_over_60': is_yes(scenario['60-or-over']),
        'on_passported_benefits': on_passported_benefits(benefits),
        'on_nass_benefits': on_nass_benefits(benefits),
        'is_partner_opponent': False
    }
    case['you'] = {
        'savings': {
            'bank_balance': money(scenario['savings']),
            'investment_balance': money(scenario['investments']),
            'credit_balance': money(scenario['owed']),
            'asset_balance': money(scenario['valuable'])
        },
        'income': {
            'earnings': money(scenario['earnings-1']),
            'self_employment_drawings': money(0),
            'benefits': money(0),
            'tax_credits': money(0),
            'child_benefits': money(0),
            'maintenance_received': money(0),
            'pension': money(0),
            'other_income': money(scenario['other-income']),
            'self_employed': is_yes(scenario['selfemp'])
        },
        'deductions': {
            'income_tax': money(scenario['tax']),
            'national_insurance': money(scenario['ni']),
            'maintenance': money(scenario['maint']),
            'childcare': money(scenario['childcare']),
            'mortgage': money(scenario['mortgage-deduction']),
            'rent': money(scenario['rent']),
            'criminal_legalaid_contributions': money(scenario['contribution'])
        }
    }
    case['partner'] = {
        'savings': {
            'bank_balance': money(scenario['psavings']),
            'investment_balance': money(scenario['pinvestments']),
            'credit_balance': money(scenario['powed']),
            'asset_balance': money(scenario['pvaluable'])
        },
        'income': {
            'earnings': money(scenario['partner-earnings']),
            'self_employment_drawings': money(0),
            'benefits': money(0),
            'tax_credits': money(0),
            'child_benefits': money(0),
            'maintenance_received': money(0),
            'pension': money(0),
            'other_income': money(scenario['partner-other-income']),
            'self_employed': is_yes(scenario['pselfemp'])
        },
        'deductions': {
            'income_tax': money(scenario['ptax']),
            'national_insurance': money(scenario['pni']),
            'maintenance': money(scenario['pmaint']),
            'childcare': money(scenario['pchildcare']),
            'mortgage': money(scenario['pmortgage']),
            'rent': money(scenario['prent']),
            'criminal_legalaid_contributions': money(scenario['pcontribution'])
        }
    }
    case['disputed_savings'] = {
        'bank_balance': money(scenario['dsavings']),
        'investment_balance': money(scenario['dinvestments']),
        'credit_balance': money(scenario['dowed']),
        'asset_balance': money(scenario['dvaluable'])
    }

    return case


def is_yes(value):
    return str(value).upper() == 'Y'


def properties(scenario):

    def property_data(i):
        prop = lambda s: scenario['prop{0}-{1}'.format(i, s)]
        if prop('value'):
            return {
                'value': money(prop('value')),
                'mortgage_left': money(prop('mortgage')),
                'share': number(prop('share')),
                'disputed': is_yes(prop('disputed')),
                'main': (i == 1)
            }

    return filter(None, map(property_data, [1, 2, 3]))


def number(s):
    try:
        n = int(s)
    except ValueError:
        return 0
    return n


def money(s):
    try:
        n = Decimal(s).quantize(Decimal('.01'))
    except (ValueError, InvalidOperation):
        return 0
    return int(n * 100)


def slugify(s):
    slug = s.strip().lower()
    slug = re.sub(r' ', '-', slug)
    slug = re.sub(r'[^\w-]+', '', slug)
    return slug


def on_passported_benefits(benefits):
    passported_benefits = [
        'income-support',
        'income-based-job-seekers-allowance',
        'income-related-employment-and-support-allowance',
        'guarantee-credit-or-universal-credit']
    return any(benefit in benefits for benefit in passported_benefits)


def on_nass_benefits(benefits):
    return 'immigrationasylum' in benefits
