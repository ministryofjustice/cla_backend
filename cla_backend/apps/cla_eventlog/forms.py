from django import forms

from cla_eventlog.registry import event_registry


class BaseCaseLogForm(forms.Form):
    """
    Use this class if your event is of one of these types:

        1. one code event where something happens and you want an event
            log to get created
        2. implicit code event where something happens and the system
            chooses which code to use.
            In this case, you need to override the `get_kwargs` method
            and add your logic. The same kwargs will be passed to the
            `Event.get_log_code`.
    """
    LOG_EVENT_KEY = None
    NOTES_MANDATORY = False

    notes = forms.CharField(required=False, max_length=5000)

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        super(BaseCaseLogForm, self).__init__(*args, **kwargs)

        if self.NOTES_MANDATORY:
            self.fields['notes'].required = True

    def get_event_key(self):
        if self.LOG_EVENT_KEY:
            return self.LOG_EVENT_KEY
        else:
            raise ValueError(
                'LOG_EVENT must be set or this method must be '
                'overridden in a subclass to return the correct event')

    def get_case(self):
        return self.case

    def get_notes(self):
        return self.cleaned_data['notes']

    def get_kwargs(self):
        return {}

    def get_context(self):
        return {}

    def save_event(self, user):
        event = event_registry.get_event(self.get_event_key())()
        event.process(
            self.get_case(), created_by=user,
            notes=self.get_notes(),
            context=self.get_context(),
            **self.get_kwargs()
        )

    def save(self, user):
        self.save_event(user)


class EventSpecificLogForm(BaseCaseLogForm):
    """
    Use this class if your event is a selectable code event where
    the client chooses which code to use.
    """
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
    """
    Not currently used.
    """
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
