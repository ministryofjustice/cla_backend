from legalaid.forms import BaseCallMeBackForm


class WebCallMeBackForm(BaseCallMeBackForm):
    def __init__(self, *args, **kwargs):
        self.requires_action_at = kwargs.pop('requires_action_at')
        super(WebCallMeBackForm, self).__init__(*args, **kwargs)

    def get_requires_action_at(self):
        return self.requires_action_at
