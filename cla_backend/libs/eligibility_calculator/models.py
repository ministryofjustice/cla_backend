from . import exceptions


class ModelMixin(object):
    PROPERTY_META = None

    def __init__(self, *args, **kwargs):
        for kw, v in kwargs.items():
            if kw not in self.PROPERTY_META:
                raise exceptions.PropertyExpectedException(
                    "'{kw}' is not a valid property for '{obj_name}'".format(
                        kw=kw, obj_name=self.__class__.__name__
                    )
                )

            fk_clazz = self.PROPERTY_META.get(kw)
            if fk_clazz:
                v = fk_clazz(**v)
            setattr(self, kw, v)

    def __getattr__(self, kw):
        obj_name = self.__class__.__name__

        if kw in self.PROPERTY_META:
            raise exceptions.PropertyExpectedException(
                "'{obj_name}' requires attribute '{kw}' and was not given at __init__".format(
                    kw=kw, obj_name=obj_name
                )
            )

        raise AttributeError(
            "'{obj_name}' object has no attribute '{kw}'".format(
                obj_name=obj_name, kw=kw
            )
        )


class Savings(ModelMixin, object):
    PROPERTY_META = {
        'bank_balance': None,
        'investment_balance': None,
        'credit_balance': None,
        'asset_balance': None
    }

    @property
    def total(self):
        return self.bank_balance + self.investment_balance + self.credit_balance + self.asset_balance


class Income(ModelMixin, object):
    PROPERTY_META = {
        'earnings': None,
        'other_income': None,
        'self_employed': None
    }

    @property
    def has_employment_earnings(self):
        return self.earnings

    @property
    def total(self):
        return self.earnings + self.other_income


class Deductions(ModelMixin, object):
    PROPERTY_META = {
        'income_tax': None,
        'national_insurance' : None,
        'maintenance': None,
        'childcare': None,
        'mortgage': None,
        'rent' : None,
        'criminal_legalaid_contributions': None
    }


class Person(ModelMixin, object):
    PROPERTY_META = {
        'income': Income,
        'savings': Savings,
        'deductions': Deductions
    }


class Facts(ModelMixin, object):
    PROPERTY_META = {
        'is_you_or_your_partner_over_60': None,
        'on_passported_benefits': None,
        'on_nass_benefits': None,
        'has_partner': None,
        'is_partner_opponent': None,
        'dependant_children': None
    }

    @property
    def has_disputed_partner(self):
        return self.has_partner and self.is_partner_opponent

    @property
    def should_aggregate_partner(self):
        if self.has_partner:
            if not self.has_disputed_partner:
                return True
        return False


class CaseData(ModelMixin, object):

    PROPERTY_META = {
        'category': None,
        'facts': Facts,
        'you': Person,
        'partner': Person,
        'property_data': None
    }

    # PROPERTY_SET = set([
    #     'category',
    #     'facts',
    #     #         'is_you_or_your_partner_over_60': None,
    #     #         'on_passported_benefits': None,
    #     #         'has_partner': None,
    #     #         'is_partner_opponent': None,
    #     #         'dependant_children': None
    #      'you',
    # # : {
    # #         # income
    # #         {
    # #             'earnings',
    # #             'other_income',
    # #             'self_employed',
    # #             },
    # #         # savings
    # #         {
    # #             'savings',
    # #             'investment_balance',
    # #             'credit_balance' ,
    # #             'asset_balance',
    # #             },
    # #         },
    #             # 'deductions',
    #             #         {
    #             #             'income_tax_and_ni': None,
    #             #             'maintenance': None,
    #             #             'mortgage_or_rent': None,
    #             #             'criminal_legalaid_contributions': None
    #             #         },
    #     'partner',
    # #         {
    # #             'income':
    # #                 {
    # #                     'partner_earnings': None,
    # #                     'partner_other_income': None,
    # #                     'partner_self_employed': None,
    # #                 },
    # #             'savings':
    # #                 {
    # #                     'partner_savings': None,
    # #                     'partner_investment_balance': None,
    # #                     'partner_credit_balance': None,
    # #                     'partner_asset_balance': None,
    # #                 },

    #                 # 'deductions',
    #                 #         {
    #                 #             'income_tax_and_ni': None,
    #                 #             'maintenance': None,
    #                 #             'mortgage_or_rent': None,
    #                 #             'criminal_legalaid_contributions': None
    #                 #         },
    # #             },
    # #     # properties
    #     'property_data'
    #      ])


    # def __getattr__(self, name):
    #     if name in self.PROPERTY_SET:
    #         raise exceptions.PropertyExpectedException(
    #             "'%s' object requires attribute '%s' and was not given at __init__" % (self.__class__.__name__, name))

    #     raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))

    # def __init__(self, **kwargs):
    #     for kw, v in kwargs.items():
    #         if kw in self.PROPERTY_SET:
    #             setattr(self, kw, v)
    #         else:
    #             raise exceptions.PropertyExpectedException('{kw} is not a valid property for Case Data'.format(kw=kw))

    # # comes from Property model
    # property_data = [('TODO value', 'TODO mortgage_left'), ('TODO value', 'TODO mortgage_left')]

    @property
    def liquid_capital(self):
        # total capital not including properties
        capital = 0

        capital += self.you.savings.total

        if self.facts.has_partner and not self.facts.has_disputed_partner:
            capital += self.partner.savings.total
        return capital

    @property
    def property_capital(self):
        properties_value = sum([d[0] for d in self.property_data])
        mortgages_left = sum([d[1] for d in self.property_data])

        return (properties_value, mortgages_left)

    @property
    def total_income(self):
        income = self.you.income.total
        if self.facts.should_aggregate_partner:
            income += self.partner.income.total
        return income
