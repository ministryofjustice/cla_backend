from cla_eventlog.forms import BaseCaseLogForm


class BaseCallMeBackForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'call_me_back'

    def get_requires_action_at(self):
        raise NotImplementedError()

    def save(self, user):
        super(BaseCallMeBackForm, self).save(user)
        dt = self.get_requires_action_at()
        self.case.set_requires_action_at(dt)
