import types

from . import exceptions


class ModelMixin(object):
    PROPERTY_META = None

    @staticmethod
    def is_a_subclass_of_model_mixin(property_meta_value):
        is_a_class = isinstance(property_meta_value, types.TypeType)
        return is_a_class and issubclass(property_meta_value, ModelMixin)

    def __init__(self, *args, **kwargs):
        for kw, v in kwargs.items():
            if kw not in self.PROPERTY_META:
                raise exceptions.PropertyExpectedException(
                    "'{kw}' is not a valid property for '{obj_name}'".format(kw=kw, obj_name=self.__class__.__name__)
                )

            property_meta_value = self.PROPERTY_META.get(kw)
            if self.is_a_subclass_of_model_mixin(property_meta_value):
                v = property_meta_value(**v)
            setattr(self, kw, v)

    # only called if the attribute is not in the class __dict__ (that is done by __get_attribute__)
    def __getattr__(self, kw):
        obj_name = self.__class__.__name__

        if kw in self.PROPERTY_META:
            property_meta_value = self.PROPERTY_META[kw]
            if self.is_a_subclass_of_model_mixin(property_meta_value):
                return property_meta_value()
            else:
                return property_meta_value

        raise AttributeError("'{obj_name}' object has no attribute '{kw}'".format(obj_name=obj_name, kw=kw))


class Savings(ModelMixin, object):
    PROPERTY_META = {"bank_balance": 0, "investment_balance": 0, "credit_balance": 0, "asset_balance": 0}

    @property
    def total(self):
        return self.bank_balance + self.investment_balance + self.credit_balance + self.asset_balance


class Income(ModelMixin, object):
    PROPERTY_META = {
        "earnings": None,
        "self_employment_drawings": None,
        "benefits": None,
        "tax_credits": None,
        "child_benefits": None,
        "maintenance_received": None,
        "pension": None,
        "other_income": None,
        "self_employed": None,
    }

    @property
    def total(self):
        return (
            self.earnings
            + self.self_employment_drawings
            + self.benefits
            + self.tax_credits
            + self.child_benefits
            + self.maintenance_received
            + self.pension
            + self.other_income
        )


class Deductions(ModelMixin, object):
    PROPERTY_META = {
        "income_tax": None,
        "national_insurance": None,
        "maintenance": None,
        "childcare": None,
        "mortgage": None,
        "rent": None,
        "criminal_legalaid_contributions": None,
    }


class Person(ModelMixin, object):
    PROPERTY_META = {"income": Income, "savings": Savings, "deductions": Deductions}


class Facts(ModelMixin, object):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("has_passported_proceedings_letter", None)
        super(Facts, self).__init__(*args, **kwargs)

    PROPERTY_META = {
        "is_you_or_your_partner_over_60": False,
        "on_passported_benefits": False,
        "on_nass_benefits": False,
        "has_partner": True,
        "is_partner_opponent": False,
        "dependants_old": None,
        "dependants_young": None,
        "has_passported_proceedings_letter": False,
        "under_18_passported": False,
        "is_you_under_18": False,
        "under_18_receive_regular_payment": False,
        "under_18_has_valuables": False,
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
        "category": "unknown",
        "facts": Facts,
        "you": Person,
        "partner": Person,
        "property_data": None,
        "disputed_savings": Savings,
    }

    def to_dict(self):
        from django.db.models.query import ValuesQuerySet

        def dump_object(obj):
            props = {}
            missing_props = {}
            for key in obj.PROPERTY_META.keys():
                if not hasattr(obj, key):
                    missing_props[key] = None
                    continue
                value = getattr(obj, key)
                missing_value = None
                if isinstance(value, ModelMixin):
                    value, missing_value = dump_object(value)
                elif isinstance(value, ValuesQuerySet):
                    value = list(value)
                props[key] = value
                if missing_value:
                    missing_props[key] = missing_value
            return props, missing_props

        data, missing_data = dump_object(self)
        return data, missing_data

    @property
    def non_disputed_non_property_capital(self):
        # total capital not including properties
        capital = 0

        capital += self.you.savings.total

        if self.facts.has_partner and not self.facts.has_disputed_partner:
            capital += self.partner.savings.total
        return capital

    @property
    def total_income(self):
        income = self.you.income.total
        if self.facts.should_aggregate_partner:
            income += self.partner.income.total
        return income
