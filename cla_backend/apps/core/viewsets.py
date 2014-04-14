
class DefaultStateFilterViewSetMixin(object):
    default_state_filter = None
    all_states = None
    state_field = 'state'


    def get_queryset(self):
        qs = super(DefaultStateFilterViewSetMixin, self).get_queryset()
        state = self.request.QUERY_PARAMS.get(self.state_field, None)
        if state in ['all', '*']:
            return qs
        if state is not None and state in self.all_states:
            return qs.filter(**{self.state_field:state})
        return qs.filter(**{self.state_field: self.default_state_filter})
