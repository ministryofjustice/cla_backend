def translate_proceeding_types(case_data):
    proceeding_types = []

    if hasattr(case_data, 'category') and getattr(case_data, 'category') == "immigration":
        proceeding_types.append(
            dict(ccms_code="IM030", client_involvement_type="A")
        )
    return {"proceeding_types": proceeding_types}
