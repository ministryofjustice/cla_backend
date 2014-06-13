import copy

case_data_dict = {
    'category': u'blah blah',
    'facts': {
        'is_you_or_your_partner_over_60': False,
        'on_passported_benefits': False,
        'on_nass_benefits' : False,
        'has_partner': False,
        'is_partner_opponent': False,
        'dependant_children': 0
    },
    'you': {
        'income': {
            'earnings': {"interval_period": "per_month",
                         "per_interval_value": 0,
                         },
            'other_income': {"interval_period": "per_month",
                             "per_interval_value": 0,
                             },
            'self_employed': False,
        },
        'savings': {
            'savings': 0,
            'investments': 0,
            'money_owed':  0,
            'valuable_items': 0,
        },
        'deductions':
            {
                'income_tax': {"interval_period": "per_month",
                               "per_interval_value": 0,
                               },
                'national_insurance': {"interval_period": "per_month",
                                       "per_interval_value": 0,
                                       },
                'maintenance': None,
                'mortgage': {"interval_period": "per_month",
                             "per_interval_value": 0,
                             },
                'rent': {"interval_period": "per_month",
                         "per_interval_value": 0,
                         },
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
