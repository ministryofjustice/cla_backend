from django.core.exceptions import ObjectDoesNotExist
from .exceptions import (
    UserIsNotOperatorException,
    OperatorDoesNotBelongToOrganisation,
    CaseNotCreatedByOperatorException,
    CaseCreatorDoesNotBelongToOrganisation,
)


def case_organisation_matches_user_organisation(case, user):
    try:
        current_operator_organisation = user.operator.organisation
    except ObjectDoesNotExist:
        raise UserIsNotOperatorException("Current user is not an operator or")
    if current_operator_organisation is None:
        raise OperatorDoesNotBelongToOrganisation("Operator does not have an organisation")

    try:
        case_creator_organisation = case.created_by.operator.organisation
    except ObjectDoesNotExist:
        raise CaseNotCreatedByOperatorException("Case created by someone not an operator")
    if case_creator_organisation is None:
        raise CaseCreatorDoesNotBelongToOrganisation("Case created by an operator that does not have an organisation")

    return case_creator_organisation == current_operator_organisation
