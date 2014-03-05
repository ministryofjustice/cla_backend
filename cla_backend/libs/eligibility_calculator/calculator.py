from . import constants


class EligibilityChecker(object):
    def __init__(self, case_data):
        super(EligibilityChecker, self).__init__()
        self.case_data = case_data

    @property
    def gross_income(self):
        if not hasattr(self, '_gross_income'):
            self._gross_income = self.case_data.total_income()
        return self._gross_income

    @property
    def disposable_income(self):
        if not hasattr(self, '_disposable_income'):
            gross_income = self.gross_income

            if self.case_data.has_partner:
                gross_income -= constants.disposable_income.PARTNER_ALLOWANCE

            # children

            # TODO 2 values for children...
            gross_income -= self.case_data.dependant_children * constants.disposable_income.CHILD_ALLOWANCE

            # Tax + NI
            gross_income -= self.case_data.income_tax_and_ni

            # maintenance 6.3
            gross_income -= self.case_data.maintenance

            # housing
            mortgage_or_rent = self.case_data.mortgage_or_rent  # excl housing benefit
            if not self.case_data.dependant_children:
                mortgage_or_rent = max(mortgage_or_rent, constants.disposable_income.CHILDLESS_HOUSING_CAP)
            gross_income -= mortgage_or_rent

            if not self.case_data.self_employed:
                gross_income -= constants.disposable_income.EMPLOYMENT_COSTS_ALLOWANCE

            if self.case_data.has_partner:
                if not self.case_data.has_disputed_partner() and not self.case_data.partner_self_employed:
                    gross_income -= constants.disposable_income.EMPLOYMENT_COSTS_ALLOWANCE

            # criminal
            gross_income -= self.case_data.criminal_legalaid_contributions  # not for now

            # NOTE ignoring childcare 6.5.2

            self._disposable_income = gross_income

        return self._disposable_income

    @property
    def disposable_capital_assets(self):
        if not hasattr(self, '_disposable_capital_assets'):
            # NOTE: problem in case of disputed partner (and joined savings/assets)

            disposable_capital = 0

            if not self.case_data.has_disputed_partner():
                disposable_capital += self.case_data.get_liquid_capital()

                properties_value, mortgages_left = self.case_data.get_property_capital()

                prop_capital = properties_value - min(mortgages_left, constants.disposable_capital.MORTGAGE_DISREGARD) - constants.disposable_capital.EQUITY_DISREGARD
                prop_capital = max(prop_capital, 0)

                disposable_capital += prop_capital
            else:
                raise NotImplementedError('Not supported yet')

            if self.case_data.is_you_or_your_partner_over_60:
                disposable_capital -= constants.disposable_capital.PENSIONER_DISREGARD_LIMIT_LEVELS.get(self.disposable_income, 0)

            disposable_capital = max(disposable_capital, 0)

            self._disposable_capital_assets = disposable_capital

        return self._disposable_capital_assets

    def is_gross_income_eligible(self):
        if self.case_data.on_passported_benefits:
            return True

        limit = constants.gross_income.get_limit(self.case_data.dependant_children)
        return self.gross_income <= limit

    def is_disposable_income_eligible(self):
        if self.case_data.on_passported_benefits:
            return True

        return self.disposable_income <= constants.disposable_income.LIMIT

    def is_disposable_capital_eligible(self):
        limit = constants.disposable_capital.get_limit(self.case_data.category)
        return self.disposable_capital_assets <= limit

    def is_eligible(self):
        if not self.is_disposable_capital_eligible():
            return False

        if not self.is_gross_income_eligible():
            return False

        if not self.is_disposable_income_eligible():
            return False

        return True
