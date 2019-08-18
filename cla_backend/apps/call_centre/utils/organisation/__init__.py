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
        return user.operator.is_cla_superuser

    return case_creator_organisation == current_operator_organisation


class NoOrganisationCaseReassignmentMixin(object):
    def get_case(self):
        raise NotImplementedError

    def post_save(self, obj, created=False, *args, **kwargs):
        super(NoOrganisationCaseReassignmentMixin, self).post_save(obj, created, *args, **kwargs)
        case = self.get_case()
        if not case.created_by:
            return

        user = self.request.user
        if case.created_by == user:
            return

        try:
            user_organisation = user.operator.organisation
        except Operator.DoesNotExist:
            return

        if not user_organisation:
            return

        try:
            case_organisation = case.created_by.operator.organisation
        except Operator.DoesNotExist:
            return

        if not case_organisation:
            case.created_by = user
            case.save(update_fields=["created_by"])
            # Create log event
