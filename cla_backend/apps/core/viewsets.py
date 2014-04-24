from eligibility_calculator.calculator import EligibilityChecker
from eligibility_calculator.exceptions import PropertyExpectedException

from rest_framework.decorators import action
from rest_framework.response import Response


class DefaultStateFilterViewSetMixin(object):
    default_state_filter = []
    all_states = None
    state_field = 'state'


    def get_queryset(self):
        qs = super(DefaultStateFilterViewSetMixin, self).get_queryset()
        state = self.request.QUERY_PARAMS.get(self.state_field, None)
        if state in ['all', '*']:
            return qs
        if state is not None:
            return qs.filter(**{self.state_field:state})
        if self.default_state_filter:
            return qs.filter(**{
                u'%s__in' % self.state_field: self.default_state_filter
            })
        return qs


class IsEligibleActionViewSetMixin(object):

    @action()
    def is_eligible(self, request, *args, **kwargs):
        obj = self.get_object()

        case_data = obj.to_case_data()
        ec = EligibilityChecker(case_data)

        response = None
        try:
            is_eligible = ec.is_eligible()
            response = 'yes' if is_eligible else 'no'
        except PropertyExpectedException as e:
            response = 'unknown'

        return Response({
            'is_eligible': response
        })
