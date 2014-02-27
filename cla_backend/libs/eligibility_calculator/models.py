from . import exceptions

class CaseData(object):

    PROPERTY_SET = set([
        'category',
        'dependant_children',
        'savings',
        'investments',
        'money_owed' ,
        'valuable_items',
        'earnings',
        'other_income',
        'self_employed',
        'partner_earnings',
        'partner_other_income',
        'partner_savings',
        'partner_investments',
        'partner_money_owned',
        'partner_valuable_items',
        'partner_self_employed',
        'property_data',
        'is_you_or_your_partner_over_60',
        'has_partner',
        'is_partner_opponent',
        'income_tax_and_ni',
        'maintenance',
        'mortgage_or_rent',
        'criminal_legalaid_contributions',
        'on_passported_benefits',
    ])


    def __getattr__(self, name):
        if name in self.PROPERTY_SET:
            raise exceptions.PropertyExpectedException(
                "'%s' object requires attribute '%s' and was not given at __init__" % (self.__class__.__name__, name))

        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))

    def __init__(self, **kwargs):
        for kw, v in kwargs.items():
            if kw in self.PROPERTY_SET:
                setattr(self, kw, v)
            else:
                raise AttributeError('{kw} is not a valid property for Case Data'.format(kw=kw))

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
        return self.has_partner and self.is_partner_opponent

    def get_liquid_capital(self):
        # total capital not including properies
        capital = 0

        capital += self.savings + self.investments + self.money_owed + self.valuable_items

        if self.has_partner:
            capital += self.partner_savings + self.partner_investments + self.partner_money_owed + self.partner_valuable_items
        return capital

    def get_property_capital(self):
        properties_value = sum([d[0] for d in self.property_data])
        mortgages_left = sum([d[1] for d in self.property_data])

        return (properties_value, mortgages_left)

    def total_income(self):
        income = self.earnings + self.other_income
        if self.has_partner:
            if not self.has_disputed_partner():
                income += self.partner_earnings + self.partner_other_income
        return income
