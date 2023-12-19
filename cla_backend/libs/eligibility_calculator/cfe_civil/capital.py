from cla_backend.libs.eligibility_calculator.cfe_civil.property import PropertyTranslator
from cla_backend.libs.eligibility_calculator.cfe_civil.savings import SavingsTranslator


class CapitalTranslator(object):
    def __init__(self, case_data, person):
        self._case_data = case_data
        self._person = person

    def is_complete(self):
        return self._is_savings_complete() and self._is_property_complete()

    def _is_savings_complete(self):
        return self._person is not None and hasattr(self._person, "savings") and self._savings_translator.is_complete()

    def _is_property_complete(self):
        return hasattr(self._case_data, "property_data") and self._property_translator.is_complete()

    @property
    def _savings_translator(self):
        return SavingsTranslator(self._person.savings)

    @property
    def _property_translator(self):
        return PropertyTranslator(self._case_data.property_data)

    def translate(self):
        request_data = {}
        if self._is_savings_complete():
            request_data.update(self._savings_translator.translate())

        if self._is_property_complete():
            request_data.update(self._property_translator.translate())
        return request_data
