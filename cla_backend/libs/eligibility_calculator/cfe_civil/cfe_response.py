class CfeResponse(object):
    def __init__(self, cfe_response_dict):
        self._cfe_data = cfe_response_dict

    @property
    def overall_result(self):
        return self._cfe_data['result_summary']['overall_result']['result']

    @property
    def employment_allowance(self):
        value = self._cfe_data['result_summary']['disposable_income']['employment_income']['fixed_employment_deduction']
        if value < 0:
            return -value
        else:
            return value

    @property
    def gross_upper_threshold(self):
        return self._cfe_data['result_summary']['gross_income']['proceeding_types'][0]['upper_threshold']

    def applicant_details(self):
        return self._cfe_data['assessment']['applicant']

    @property
    def pensioner_disregard(self):
        return self._cfe_data['result_summary']['capital']['pensioner_capital_disregard']

    @property
    def disposable_capital_assets(self):
        return self._cfe_data['result_summary']['capital']['combined_assessed_capital']

    @property
    def property_equities(self):
        properties = []
        cfe_properties = self._cfe_data['assessment']['capital']['capital_items']['properties']
        if cfe_properties['main_home']:
            properties.append(cfe_properties['main_home'])
        if cfe_properties['additional_properties']:
            properties.extend(cfe_properties['additional_properties'])
        return [property['assessed_equity'] for property in properties
                if property['assessed_equity'] > 0]

    @property
    def property_capital(self):
        return sum(self.property_equities)

    @property
    def liquid_capital(self):
        return self._cfe_data['result_summary']['capital']['total_liquid']

    @property
    def gross_income(self):
        return self._cfe_data['result_summary']['gross_income']['combined_total_gross_income']

    @property
    def disposable_income(self):
        return self._cfe_data['result_summary']['disposable_income']['combined_total_disposable_income']

    @property
    def non_liquid_capital(self):
        return self._cfe_data['result_summary']['capital']['total_non_liquid']

    @property
    def vehicle_capital(self):
        return self._cfe_data['result_summary']['capital']['total_vehicle']
