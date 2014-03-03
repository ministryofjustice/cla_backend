
case_data_dict =  {'category': u'blah blah',
                   'criminal_legalaid_contributions': 0,
                   'dependant_children': 0,
                   'earnings': 165700,
                   'has_partner': False,
                   'income_tax_and_ni': 0,
                   'investments': 220000,
                   'is_partner_opponent': False,
                   'is_you_or_your_partner_over_60': False,
                   'maintenance': 0,
                   'money_owed': 220000,
                   'mortgage_or_rent': 0,
                   'on_passported_benefits': False,
                   'other_income': 10000,
                   'property_data': [(22, 0, 100)],
                   'savings': 220000,
                   'self_employed': False,
                   'valuable_items': 220000}



def get_default_case_data(**kwargs):
    """
    gives default case_data with each kwarg
    overridden

    :param kwargs: things to overwrite in the default case_data
    :return: CaseData object with default values
    """
    defaults = case_data_dict.copy()
    defaults.update(kwargs)
    return defaults