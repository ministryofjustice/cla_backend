from cla_eventlog.forms import EventSpecificLogForm, BaseCaseLogForm


class RejectCaseForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'reject_case'


class AcceptCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'accept_case'


class CloseCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'close_case'
