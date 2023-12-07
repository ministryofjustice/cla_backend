import json


class CfeResponse(object):
    def __init__(self, cfe_response_json):
        self._cfe_data = json.loads(cfe_response_json)

    def overall_result(self):
        return self._cfe_data['result_summary']['overall_result']['result']

    def gross_upper_threshold(self):
        return self._cfe_data['result_summary']['gross_income']['proceeding_types'][0]['upper_threshold']