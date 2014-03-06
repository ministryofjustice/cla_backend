from . import exceptions

class CaseData(object):

    # PROPERTY_TEMPLATE = {
    #     'category': None,
    #     # facts
    #     'facts': {
    #         'is_you_or_your_partner_over_60': None,
    #         'on_passported_benefits': None,
    #         'has_partner': None,
    #         'is_partner_opponent': None,
    #         'dependant_children': None
    #     },
    #
    #     'deductions':
    #         {
    #             'income_tax_and_ni': None,
    #             'maintenance': None,
    #             'mortgage_or_rent': None,
    #             'criminal_legalaid_contributions': None
    #         },
    #     'you': {
    #         # income
    #         {
    #             'earnings',
    #             'other_income',
    #             'self_employed',
    #             },
    #         # savings
    #         {
    #             'savings',
    #             'investments',
    #             'money_owed' ,
    #             'valuable_items',
    #             },
    #         },
    #
    #     'partner':
    #         {
    #             'income':
    #                 {
    #                     'partner_earnings': None,
    #                     'partner_other_income': None,
    #                     'partner_self_employed': None,
    #                 },
    #             'savings':
    #                 {
    #                     'partner_savings': None,
    #                     'partner_investments': None,
    #                     'partner_money_owed': None,
    #                     'partner_valuable_items': None,
    #                 },
    #             },
    #     # properties
    #     'property_data': None,
    #     }


    # def __getattr__(self, name):
    #     if name in self.PROPERTY_SET:
    #         raise exceptions.PropertyExpectedException(
    #             "'%s' object requires attribute '%s' and was not given at __init__" % (self.__class__.__name__, name))
    #
    #     raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))

    def __init__(self, **kwargs):
        for kw, v in kwargs.items():
            setattr(self, kw, v)

        # if sum([v for k,v in kwargs.items() if k.startswith('partner')]) and not kwargs.get('has_partner', False):
        #     raise exceptions.InvalidStateException('You have specified partner capital fields but also specified has_partner = False')
        #
        # for kw, v in kwargs.items():
        #     if kw in self.PROPERTY_SET:
        #         setattr(self, kw, v)
        #     else:
        #         raise exceptions.PropertyExpectedException('{kw} is not a valid property for Case Data'.format(kw=kw))

    # # EligibilityCheck
    # category = None
    # dependant_children = 0 # EligibilityCheck.dependent_young + dependant_old
    #
    # # Finances
    # savings = 0 # Finances.bank_balance
    # investments = 0 # Finances.investment balance
    # money_owned = 0 # credit balance
    # valuable_items = 0 # asset balance
    # earnings = 0 # Finances.earnings
    # other_income = 0 # Finances.other_income
    # self_employed = False # Finances.self_employed
    #
    # partner_earnings = 0
    # partner_other_income = 0
    # partner_savings = 0
    # partner_investments = 0
    # partner_money_owned = 0
    # partner_valuable_items = 0
    # partner_self_employed = False
    #
    # # comes from Property model
    # property_data = [('TODO value', 'TODO mortgage_left'), ('TODO value', 'TODO mortgage_left')]
    #
    # # asked but not saved
    # is_you_or_your_partner_over_60 = False
    # has_partner = False
    #
    # # not asked, not saved
    # is_partner_opponent = False # assume NO for now (debt cases)
    # income_tax_and_ni = 0 # waiting for design
    # maintenance = 0 # waiting for design
    # mortgage_or_rent = 0 # waiting for design
    # criminal_legalaid_contributions = 0 # waiting for design
    # on_passported_benefits = False # need now

    def has_disputed_partner(self):
        return self.facts['has_partner'] and self.facts['is_partner_opponent']

    def get_liquid_capital(self):
        # total capital not including properties
        capital = 0

        capital += self.you['savings']['savings'] + self.you['savings']['investments'] + self.you['savings']['money_owed'] + self.you['savings']['valuable_items']

        if self.facts['has_partner'] and self.partner:
            capital += self.partner['savings']['savings']+ self.partner['savings']['investments'] + self.partner['savings']['money_owed'] + self.partner['savings']['valuable_items']
        return capital

    def get_property_capital(self):
        properties_value = sum([d[0] for d in self.property_data])
        mortgages_left = sum([d[1] for d in self.property_data])

        return (properties_value, mortgages_left)

    def total_income(self):
        income = self.you['income']['earnings'] + self.you['income']['other_income']
        if self.facts['has_partner']:
            if not self.has_disputed_partner():
                income += self.partner['income']['earnings'] + self.partner['income']['other_income']
        return income
