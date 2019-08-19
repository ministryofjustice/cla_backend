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


class NoOrganisationCaseAssignCurrentOrganisationMixin(object):
    def get_case(self):
        raise NotImplementedError

    def post_save(self, obj, created=False, *args, **kwargs):
        super(NoOrganisationCaseAssignCurrentOrganisationMixin, self).post_save(obj, created, *args, **kwargs)
        case = self.get_case()
        if case.organisation:
            return

        user = self.request.user
        if case.created_by == user:
            return

        try:
            organisation = user.operator.organisation
        except Operator.DoesNotExist:
            return

        if not organisation:
            return

        case.organisation = organisation
        case.save(update_fields=["organisation"])
        # Create log event
        from cla_eventlog import event_registry

        notes = u"Case organisation set to {organisation}".format(organisation=organisation)
        event = event_registry.get_event("case")()
        event.process(case, created_by=user, notes=notes, complaint=obj, code="CASE_ORGANISATION_SET")
