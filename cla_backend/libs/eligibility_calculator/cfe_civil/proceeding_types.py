CATEGORY_TO_PROCEEDING_TYPE = {"immigration": {"ccms_code": "IM030", "client_involvement_type": "A"}}

DEFAULT_PROCEEDING_TYPE = {"ccms_code": "SE013", "client_involvement_type": "A"}


def translate_proceeding_types(category):
    proceeding_types = []

    if category == "immigration":
        proceeding_types.append(dict(CATEGORY_TO_PROCEEDING_TYPE["immigration"]))
    else:
        proceeding_types.append(DEFAULT_PROCEEDING_TYPE)
    return proceeding_types
