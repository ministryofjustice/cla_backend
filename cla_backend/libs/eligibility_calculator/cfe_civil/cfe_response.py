class CfeResponse(object):
    def __init__(self, cfe_response_dict):
        self._cfe_data = cfe_response_dict

    @property
    def overall_result(self):
        return self._result_summary["overall_result"]["result"]

    @property
    def employment_allowance(self):
        value = self._result_summary["disposable_income"]["employment_income"]["fixed_employment_deduction"]
        if value < 0:
            return -value
        else:
            return value

    @property
    def gross_upper_threshold(self):
        return self._result_summary["gross_income"]["proceeding_types"][0]["upper_threshold"]

    @staticmethod
    def _result_to_tristate(test_result):
        """Takes the result of one of the three tests, and converts to True/False/None"""
        if test_result in ("eligible", "contribution_required"):
            return True
        elif test_result == "inelgible":
            return False
        return None  # not_yet_known/not_calculated

    @property
    def is_gross_eligible(self):
        return CfeResponse._result_to_tristate(self._result_summary["gross_income"]["proceeding_types"][0])

    @property
    def is_disposable_eligible(self):
        return CfeResponse._result_to_tristate(self._result_summary["disposable_income"]["proceeding_types"][0])

    @property
    def is_capital_eligible(self):
        return CfeResponse._result_to_tristate(self._result_summary["capital"]["proceeding_types"][0])

    def applicant_details(self):
        return self._cfe_data["assessment"]["applicant"]

    @property
    def pensioner_disregard(self):
        return self._result_summary["capital"]["pensioner_capital_disregard"]

    @property
    def disposable_capital_assets(self):
        return self._result_summary["capital"]["combined_assessed_capital"]

    @property
    def property_equities(self):
        properties = []
        cfe_properties = self._cfe_data["assessment"]["capital"]["capital_items"]["properties"]
        if cfe_properties["main_home"]:
            properties.append(cfe_properties["main_home"])
        if cfe_properties["additional_properties"]:
            properties.extend(cfe_properties["additional_properties"])
        return [property["assessed_equity"] for property in properties]

    @property
    def property_capital(self):
        return sum(self.property_equities)

    @property
    def gross_income(self):
        return self._result_summary["gross_income"]["combined_total_gross_income"]

    @property
    def disposable_income(self):
        return self._result_summary["disposable_income"]["combined_total_disposable_income"]

    @property
    def liquid_capital(self):
        return self._result_capital_aggregated("total_liquid")

    @property
    def non_liquid_capital(self):
        return self._result_capital_aggregated("total_non_liquid")

    @property
    def vehicle_capital(self):
        return self._result_capital_aggregated("total_vehicle")

    def _result_capital_aggregated(self, key):
        return self._result_capital[key] + self._result_partner_capital[key]

    @property
    def _result_capital(self):
        return self._cfe_data["result_summary"]["capital"]

    @property
    def _result_partner_capital(self):
        if "partner_capital" in self._result_summary:
            return self._result_summary["partner_capital"]
        else:
            return {"total_vehicle": 0, "total_liquid": 0, "total_non_liquid": 0}

    @property
    def _result_summary(self):
        return self._cfe_data["result_summary"]

    @property
    def dependants_allowance(self):
        return self._result_summary["disposable_income"]["dependant_allowance"]

    @property
    def partner_allowance(self):
        return self._result_summary["disposable_income"]["partner_allowance"]
