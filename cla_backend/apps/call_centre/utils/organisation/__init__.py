from legalaid.models import Case
from call_centre.models import Operator
from cla_eventlog import event_registry


class CaseOrganisationAssignCurrentOrganisationMixin(object):
    def get_case(self, obj):
        if hasattr(obj, "case"):
            try:
                return obj.case
            except Case.DoesNotExist:
                pass

        if "case_reference" not in self.kwargs:
            return None
        try:
            return Case.objects.get(reference=self.kwargs.get("case_reference"))
        except Case.DoesNotExist:
            return None

    def set_case_organisation(self, case, save=True):
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
        if save:
            case.save(update_fields=["organisation"])

        # Create event log if the case is being updated
        if case.pk:
            notes = u"Case organisation set to {organisation}".format(organisation=organisation)
            event = event_registry.get_event("case")()
            event.process(case, created_by=user, notes=notes, complaint=case, code="CASE_ORGANISATION_SET")

    def pre_save(self, obj, **kwargs):
        super(CaseOrganisationAssignCurrentOrganisationMixin, self).pre_save(obj, **kwargs)
        if isinstance(obj, Case):
            case = obj
        else:
            case = self.get_case(obj)

        if not case:
            return

        # When current object is a case then we don't need to save it as we are in its pre_save
        # but have to explicitly save it for other objects
        save = not isinstance(obj, Case)
        self.set_case_organisation(case, save)
