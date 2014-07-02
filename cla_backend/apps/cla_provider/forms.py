from cla_eventlog.forms import EventSpecificLogForm, BaseCaseLogForm


class RejectCaseForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'reject_case'

    def save(self, user):
        self.case.reject()

        super(RejectCaseForm, self).save(user)  # saves the outcome


class AcceptCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'accept_case'

    def save(self, user):
        self.case.accept()

        super(AcceptCaseForm, self).save(user)  # saves the outcome


class CloseCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'close_case'

    def save(self, user):
        self.case.close()

        super(CloseCaseForm, self).save(user)  # saves the outcome
