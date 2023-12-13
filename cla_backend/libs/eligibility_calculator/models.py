from . import exceptions


class ModelMixin(object):
    PROPERTY_META = None

    def __init__(self, *args, **kwargs):
        for kw, v in kwargs.items():
            if kw not in self.PROPERTY_META:
                raise exceptions.PropertyExpectedException(
                    "'{kw}' is not a valid property for '{obj_name}'".format(kw=kw, obj_name=self.__class__.__name__)
                )

            fk_clazz = self.PROPERTY_META.get(kw)
            if fk_clazz:
                v = fk_clazz(**v)
            setattr(self, kw, v)

    def __getattr__(self, kw):
        obj_name = self.__class__.__name__

        if kw in self.PROPERTY_META:
            raise exceptions.PropertyExpectedException(
                "'{obj_name}' requires attribute '{kw}' and was not given at __init__".format(kw=kw, obj_name=obj_name)
            )

        raise AttributeError("'{obj_name}' object has no attribute '{kw}'".format(obj_name=obj_name, kw=kw))


class Savings(ModelMixin, object):
    PROPERTY_META = {"bank_balance": None, "investment_balance": None, "credit_balance": None, "asset_balance": None}

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
    def has_employment_earnings(self):
        return self.earnings

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
        "is_you_or_your_partner_over_60": None,
        "on_passported_benefits": None,
        "on_nass_benefits": None,
        "has_partner": None,
        "is_partner_opponent": None,
        "dependants_old": None,
        "dependants_young": None,
        "has_passported_proceedings_letter": None,
        "under_18_passported": None,
        "is_you_under_18": None,
        "under_18_receive_regular_payment": None,
        "under_18_has_valuables": None,
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

    @property
    def dependant_children(self):
        return self.dependants_old + self.dependants_young


class CaseData(ModelMixin, object):

    PROPERTY_META = {
        "category": None,
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
            for key in obj.PROPERTY_META.keys():
                try:
                    value = getattr(obj, key)
                except Exception:
                    value = None
                if isinstance(value, ModelMixin):
                    value = dump_object(value)
                elif isinstance(value, ValuesQuerySet):
                    value = list(value)
                props[key] = value
            return props

        data = dump_object(self)
        return data

    @property
    def non_disputed_liquid_capital(self):
        # total capital not including properties
        capital = 0

        capital += self.you.savings.total

        if self.facts.has_partner and not self.facts.has_disputed_partner:
            capital += self.partner.savings.total
        return capital

    @property
    def disputed_liquid_capital(self):
        if hasattr(self, "disputed_savings") and self.disputed_savings:
            return self.disputed_savings.total
        return 0

    @property
    def total_income(self):
        income = self.you.income.total
        if self.facts.should_aggregate_partner:
            income += self.partner.income.total
        return income
