from . import constants


class EligibilityChecker(object):
	def __init__(self, case_data):
		super(EligibilityChecker, self).__init__()
		self.case_data = case_data

	def is_gross_income_eligible(self):
		gross_income = self.case_data.total_income()

		if gross_income > constants.gross_income.get_limit(self.case_data.dependant_children):
			eligible = False
		else:
			eligible = True

		return (eligible, gross_income)

	def _get_disposable_income(self, gross_income):
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

		if not self.case_data.has_disputed_partner() and not self.case_data.partner_self_employed:
			gross_income -= constants.disposable_income.EMPLOYMENT_COSTS_ALLOWANCE

		# criminal
		gross_income -= self.case_data.criminal_legalaid_contributions  # not for now

		# NOTE ignoring childcare 6.5.2

		return gross_income

	def is_disposable_income_eligible(self, gross_income):
		disposable_income = self._get_disposable_income(gross_income)

		return (disposable_income <= constants.disposable_income.LIMIT, disposable_income)

	def get_disposable_capital_assets(self, disposable_income):
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
			disposable_capital -= constants.disposable_capital.PENSIONER_DISREGARD_LIMIT_LEVELS.get(disposable_income, 0)

		disposable_capital = max(disposable_capital, 0)

		return disposable_capital

	def is_disposable_capital_eligible(self, disposable_income):
		if self.get_disposable_capital_assets(disposable_income) > constants.disposable_capital.get_limit(self.case_data.category):
			return False

		return True

	def is_eligible(self):
		disposable_income = 0
		if not self.case_data.on_passported_benefits():
			is_gross_income_eligible, gross_income = self.is_gross_income_eligible()
			if not is_gross_income_eligible:
				return False

			is_disposable_income_eligible, disposable_income = self.is_disposable_income_eligible(gross_income)
			if not is_disposable_income_eligible:
				return False

		if not self.is_disposable_capital_eligible(disposable_income):
			return False

		return True
