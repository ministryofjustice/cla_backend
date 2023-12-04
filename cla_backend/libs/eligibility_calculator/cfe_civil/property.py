from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds

def convert_house(house_data):
    return {
        "value": pence_to_pounds(house_data['value']),
        "outstanding_mortgage": pence_to_pounds(house_data['mortgage_left']),
        "percentage_owned": house_data['share'],
        "shared_with_housing_assoc": False,
        "subject_matter_of_dispute": house_data['disputed']
    }

def translate_property(property_data):
    main_homes = [x for x in property_data if x['main'] == True]
    non_mains = [x for x in property_data if x['main'] == False]
    if (len(main_homes) > 0):
        main_home_data = main_homes[0]
        main_home = convert_house(main_home_data)
        # all main homes after the first are additional properties
        non_mains = non_mains + main_homes[1:]
    else:
        main_home = None
    additional_houses = map(convert_house, non_mains)

    if main_home:
        return {
            "properties": {
                "main_home": main_home,
                "additional_properties": additional_houses
            }
        }
    else:
        return {
            "properties": {
                "additional_properties": additional_houses
            }
        }
