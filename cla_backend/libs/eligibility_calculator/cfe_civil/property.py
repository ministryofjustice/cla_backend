from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds


def _convert_house(house_data):
    return {
        "value": pence_to_pounds(house_data['value']),
        "outstanding_mortgage": pence_to_pounds(house_data['mortgage_left']),
        "percentage_owned": house_data['share'],
        "shared_with_housing_assoc": False,
        "subject_matter_of_dispute": house_data['disputed']
    }


def _valid_house(house_data):
    return 'main' in house_data and \
        house_data['value'] is not None and \
        house_data['mortgage_left'] is not None and \
        house_data['share'] is not None and \
        'disputed' in house_data


_CFE_PROPERTY_KEY = "properties"


class PropertyTranslator(object):
    def __init__(self, possible_property_data):
        self._possible_property_data = possible_property_data
        self._property_data = [house for house in self._possible_property_data if _valid_house(house)]

    def is_complete(self):
        return len(self._possible_property_data) == len(self._property_data)

    def translate(self):
        main_homes = [x for x in self._property_data if x['main']]
        non_mains = [x for x in self._property_data if not x['main']]
        if (len(main_homes) > 0):
            main_home_data = main_homes[0]
            main_home = _convert_house(main_home_data)
            # all main homes after the first are additional properties
            non_mains = non_mains + main_homes[1:]
        else:
            main_home = None
        additional_houses = map(_convert_house, non_mains)

        if main_home:
            return {
                _CFE_PROPERTY_KEY: {
                    "main_home": main_home,
                    "additional_properties": additional_houses
                }
            }
        else:
            return {
                _CFE_PROPERTY_KEY: {
                    "additional_properties": additional_houses
                }
            }
