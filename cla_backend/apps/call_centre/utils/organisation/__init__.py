from call_centre.models import Operator

from .exceptions import UserIsNotOperatorException


def case_organisation_matches_user_organisation(case, user):
    # Return True when:
    # Current operator organisations matches case creator organisation
    # Case creator does not have organisation

    if not case.created_by:
        return True

    try:
        case_creator_organisation = case.created_by.operator.organisation
    except Operator.DoesNotExist:
        return True

    if case_creator_organisation is None:
        return True

    try:
        current_operator_organisation = user.operator.organisation
    except Operator.DoesNotExist:
        raise UserIsNotOperatorException("Case creator has organisation but current user is not an operator")

    if current_operator_organisation is None:
        return False

    return case_creator_organisation == current_operator_organisation
