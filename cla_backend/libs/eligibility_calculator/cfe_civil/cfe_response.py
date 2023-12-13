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
