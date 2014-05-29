from django import forms

from legalaid.models import CaseLog, CaseLogType


class BaseCaseLogForm(forms.Form):
    CASELOGTYPE_CODE = None

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        super(BaseCaseLogForm, self).__init__(*args, **kwargs)

    def get_logtype(self):
        if self.CASELOGTYPE_CODE:
            return CaseLogType.objects.get(code=self.CASELOGTYPE_CODE)
        else:
            raise ValueError(
                'CASELOGTYPE_CODE must be set or this method must be '
                'overridden in a subclass to return the correct CaseLogType instance')

    def get_notes(self):
        raise NotImplementedError

    def save(self, user):
        CaseLog.objects.create(
            case=self.case, created_by=user,
            logtype=self.get_logtype(), notes=self.get_notes()
        )


class OutcomeForm(BaseCaseLogForm):
    outcome_code = forms.ModelChoiceField(
        queryset=CaseLogType.objects, to_field_name='code', empty_label=None
    )
    outcome_notes = forms.CharField(required=False, max_length=500)

    def __init__(self, *args, **kwargs):
        super(OutcomeForm, self).__init__(*args, **kwargs)

        self.fields['outcome_code'].queryset = self.get_outcome_code_queryset()

    def get_outcome_code_queryset(self):
        return CaseLogType.objects.filter(subtype='outcome')

    def get_logtype(self):
        return self.cleaned_data['outcome_code']

    def get_notes(self):
        return self.cleaned_data['outcome_notes']
