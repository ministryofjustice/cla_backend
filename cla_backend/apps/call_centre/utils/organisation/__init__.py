from legalaid.models import Case
from call_centre.models import Operator
from cla_eventlog import event_registry


class CaseOrganisationAssignCurrentOrganisationMixin(object):
    def perform_create(self, serializer):
        obj = super(CaseOrganisationAssignCurrentOrganisationMixin, self).perform_create(serializer)
        self.save_organisation(serializer.validated_data)
        return obj

    def perform_update(self, serializer):
        super(CaseOrganisationAssignCurrentOrganisationMixin, self).perform_update(serializer)
        self.save_organisation(serializer.validated_data, self.get_object())

    def get_case(self, validated_data, obj=None):
        if obj and hasattr(obj, "case"):
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

    def set_case_organisation(self, case):
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
        case.save(update_fields=["organisation"])

        # Create event log if the case is being updated
        notes = u"Case organisation set to {organisation}".format(organisation=organisation)
        event = event_registry.get_event("case")()
        event.process(case, created_by=user, notes=notes, complaint=case, code="CASE_ORGANISATION_SET")

    def save_organisation(self, validated_data, obj=None):

        if isinstance(obj, Case):
            case = obj
        else:
            case = self.get_case(validated_data, obj=obj)

        if not case:
            return

        self.set_case_organisation(case)
