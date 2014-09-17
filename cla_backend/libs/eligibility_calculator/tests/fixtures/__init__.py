import copy

case_data_dict = {
    'category': u'blah blah',
    'facts': {
        'is_you_or_your_partner_over_60': False,
        'on_passported_benefits': False,
        'on_nass_benefits' : False,
        'has_partner': False,
        'is_partner_opponent': False,
        'dependants_young': 0,
        'dependants_old': 0
    },
    'you': {
        'income': {
            'earnings': 0,
            'self_employment_drawings': 0,
            'benefits': 0,
            'tax_credits': 0,
            'child_benefits': 0,
            'maintenance_received': 0,
            'pension': 0,
            'other_income': 0,
            'self_employed': False,
        },
        'savings': {
            'bank_balance': 0,
            'investment_balance': 0,
            'credit_balance':  0,
            'asset_balance': 0,
        },
        'deductions':
            {
                'income_tax': 0,
                'national_insurance': 0,
                'maintenance': 0,
                'mortgage': 0,
                'rent': 0,
                'childcare': 0,
                'criminal_legalaid_contributions': 0,
            },
    },
    'property_data': [],
    # 'property_data': [(22, 0, 100)],
}



def get_default_case_data(**kwargs):
    """
    gives default case_data with each kwarg
    overridden, use __ to access nested dictionaries
    e.g. you__income__earnings

    :param kwargs: things to overwrite in the default case_data
    :return: CaseData object with default values
    """
    defaults = copy.deepcopy(case_data_dict)
    if len(kwargs):
        keys_vals = sorted([(kw.split('__'), v) for kw, v in kwargs.items()], key=lambda x: len(x[0]))
        for (k, v) in keys_vals:
            level = defaults
            for i in range(0,len(k)):
                if k[0:i+1] == k:
                    level[k[i]] = v
                else:
                    new_level = level.get(k[i])
                    if new_level == None and not i == len(k):
                        level[k[i]] = {}
                    level = level[k[i]]

    return defaults
