from call_centre.models import Operator

from .exceptions import (
    UserIsNotOperatorException,
    OperatorDoesNotBelongToOrganisation,
    CaseNotCreatedByOperatorException,
    CaseCreatorDoesNotBelongToOrganisation,
)


def case_organisation_matches_user_organisation(case, user):
    try:
        current_operator_organisation = user.operator.organisation
    except Operator.DoesNotExist:
        raise UserIsNotOperatorException("Current user is not an operator")

    if current_operator_organisation is None:
        raise OperatorDoesNotBelongToOrganisation("Operator does not have an organisation")

    try:
        # Case creator is not an operator
        case_creator_organisation = case.created_by.operator.organisation
    except Operator.DoesNotExist:
        raise CaseNotCreatedByOperatorException("Case created by someone not an operator")

    if case_creator_organisation is None:
        raise CaseCreatorDoesNotBelongToOrganisation("Case created by an operator that does not have an organisation")

    return case_creator_organisation == current_operator_organisation
