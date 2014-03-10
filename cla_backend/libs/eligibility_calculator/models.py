from . import exceptions

class CaseData(object):

    PROPERTY_SET = set([
        'category',
        'facts',
        #         'is_you_or_your_partner_over_60': None,
        #         'on_passported_benefits': None,
        #         'has_partner': None,
        #         'is_partner_opponent': None,
        #         'dependant_children': None
         'you',
    # : {
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
                # 'deductions',
                #         {
                #             'income_tax_and_ni': None,
                #             'maintenance': None,
                #             'mortgage_or_rent': None,
                #             'criminal_legalaid_contributions': None
                #         },
        'partner',
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

                    # 'deductions',
                    #         {
                    #             'income_tax_and_ni': None,
                    #             'maintenance': None,
                    #             'mortgage_or_rent': None,
                    #             'criminal_legalaid_contributions': None
                    #         },
    #             },
    #     # properties
        'property_data'
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
                raise exceptions.PropertyExpectedException('{kw} is not a valid property for Case Data'.format(kw=kw))

    # # comes from Property model
    # property_data = [('TODO value', 'TODO mortgage_left'), ('TODO value', 'TODO mortgage_left')]

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
        income = self.you.get('income', {}).get('earnings', 0) + self.you.get('income', {}).get('other_income', 0)
        if self.facts['has_partner']:
            if not self.has_disputed_partner():
                income += self.partner.get('income', {}).get('earnings', 0) + self.partner.get('income', {}).get('other_income', 0)
        return income
