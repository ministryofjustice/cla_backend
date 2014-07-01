from cla_eventlog.constants import LOG_ROLES
from django import forms
from cla_eventlog.registry import event_registry


class BaseCaseLogForm(forms.Form):
    LOG_EVENT_KEY = None

    notes = forms.CharField(required=False, max_length=500)

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        super(BaseCaseLogForm, self).__init__(*args, **kwargs)

    def get_event_key(self):
        if self.LOG_EVENT_KEY:
            return self.LOG_EVENT_KEY
        else:
            raise ValueError(
                'LOG_EVENT must be set or this method must be '
                'overridden in a subclass to return the correct event')

    def get_notes(self):
        return self.cleaned_data['notes']

    def get_kwargs(self):
        return {}

    def save(self, user):
        event = event_registry.get_event(self.get_event_key())()
        event.process(self.case, created_by=user,
                           notes=self.get_notes(), **self.get_kwargs())


class EventSpecificLogForm(BaseCaseLogForm):
    event_code = forms.ChoiceField(
        choices=()
    )

    def __init__(self, *args, **kwargs):
        super(EventSpecificLogForm, self).__init__(*args, **kwargs)
        self.fields['event_code'].choices = self.get_event_code_choices()

    def get_event_code_choices(self):
        event = event_registry.get_event(self.get_event_key())()
        return [(code,code) for code in event.codes.keys()]

    def get_event_code(self):
        return self.cleaned_data['event_code']

    def get_kwargs(self):
        kwargs = super(EventSpecificLogForm, self).get_kwargs()
        kwargs['code'] = self.get_event_code()
        return kwargs


class SelectableEventLogForm(EventSpecificLogForm):
    ROLE = None

    def get_role(self):
        if self.ROLE:
            return self.ROLE
        else:
            raise NotImplementedError('Role must be set or this method must'
            'be overwritten in a subclass')

    def get_event_code_choices(self):
        selectable_events = event_registry.get_selectable_events(self.get_role())
        choices = []
        for event_key, codes in selectable_events.items():
            [choices.append(('%s:%s' % (event_key, code), '%s' % code)) for code in codes]
        return choices

    def get_event_code(self):
        return self.cleaned_data['event_code_']

    def get_event_key(self):
        return self.cleaned_data.get('event_key')

    def clean(self):
        cleaned_data = super(SelectableEventLogForm, self).clean()
        event_key, event_code = cleaned_data['event_code'].split(':')
        cleaned_data['event_key']  = event_key
        cleaned_data['event_code_'] = event_code

        return cleaned_data
