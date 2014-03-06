import operator

case_data_dict = {
    'category': u'blah blah',
    'facts': {
        'is_you_or_your_partner_over_60': False,
        'on_passported_benefits': False,
        'has_partner': False,
        'is_partner_opponent': False,
        'dependant_children': 0
    },
    'you': {
        'income': {
            'earnings': 165700,
            'other_income': 10000,
            'self_employed': False,
        },
        'savings': {
            'savings': 220000,
            'investments': 220000,
            'money_owed': 220000 ,
            'valuable_items': 220000,
        },
        'deductions':
            {
                'income_tax_and_ni': 0,
                'maintenance': None,
                'mortgage_or_rent': 0,
                'criminal_legalaid_contributions': 0,
            },
    },
    'property_data': [(22, 0, 100)],
}



def get_default_case_data(**kwargs):
    """
    gives default case_data with each kwarg
    overridden, use __ to access nested dictionaries
    e.g. you__income__earnings

    :param kwargs: things to overwrite in the default case_data
    :return: CaseData object with default values
    """
    defaults = case_data_dict.copy()
    if len(kwargs):
        keys_vals = sorted([(kw.split('__'), v) for kw, v in kwargs.items()], key=lambda x: len(x[0]))
        for (k, v) in keys_vals:
            level = defaults
            for nesting in k:
                if nesting == k[-1]:
                    level[nesting] = v
                else:
                    new_level = level.get(nesting)
                    if not new_level:
                        level[nesting] = {}
                    level = level[nesting]

    return defaults
