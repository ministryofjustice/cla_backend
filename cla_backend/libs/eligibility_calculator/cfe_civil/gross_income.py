
from cla_backend.libs.eligibility_calculator.cfe_civil.employment import EmploymentTranslator
from cla_backend.libs.eligibility_calculator.cfe_civil.income import NonEmploymentIncomeTranslator


class GrossIncomeTranslator(object):
    def __init__(self, person):
        self._person = person

    def is_complete(self):
        return self._is_employment_complete() and self.is_non_employment_complete()

    def _is_employment_complete(self):
        return hasattr(self._person, "income") and hasattr(self._person,
                                                           "deductions") and self._employment_translator.is_complete()

    def is_non_employment_complete(self):
        return hasattr(self._person, "income") and self._other_income_translator.is_complete()

    @property
    def _employment_translator(self):
        return EmploymentTranslator(self._person.income, self._person.deductions)

    @property
    def _other_income_translator(self):
        return NonEmploymentIncomeTranslator(self._person.income)

    def translate(self):
        request_data = {}

        if self._is_employment_complete():
            request_data.update(self._employment_translator.translate())

        if self.is_non_employment_complete():
            request_data.update(self._other_income_translator.translate())

        return request_data
