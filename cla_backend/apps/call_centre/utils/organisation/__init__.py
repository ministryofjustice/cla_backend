from call_centre.models import Operator
from legalaid.models import Case


def case_organisation_matches_user_organisation(case, user):
    # Return True when:
    # Current operator organisations matches case organisation
    # Case does not have organisation
    # Current user is cla_superuser
    # Current user is not operator

    if not case.organisation:
        # Case has no organisation anyone can edit
        return True

    try:
        operator_organisation = user.operator.organisation
    except Operator.DoesNotExist:
        # user is not operator. Organisation access control only applies to operators
        return True

    if operator_organisation is None:
        return user.operator.is_cla_superuser

    return case.organisation == operator_organisation


class NoOrganisationCaseAssignCurrentOrganisationMixin(object):
    def get_case(self, obj):
        return None

    def pre_save(self, obj, **kwargs):
        super(NoOrganisationCaseAssignCurrentOrganisationMixin, self).pre_save(obj, **kwargs)
        if isinstance(obj, Case):
            case = obj
        else:
            case = self.get_case(obj)

        if not case:
            return

        if case.organisation:
            return

        user = self.request.user
        try:
            organisation = user.operator.organisation
        except Operator.DoesNotExist:
            return

        if not organisation:
            return

        case.organisation = organisation
        # When current object is a case then we don't need to save it as we are in it's pre_save
        # but have to explicitly save it for other objects
        if not isinstance(obj, Case):
            case.save(update_fields=["organisation"])

        # Create event log
        from cla_eventlog import event_registry

        notes = u"Case organisation set to {organisation}".format(organisation=organisation)
        event = event_registry.get_event("case")()
        event.process(case, created_by=user, notes=notes, complaint=case, code="CASE_ORGANISATION_SET")
