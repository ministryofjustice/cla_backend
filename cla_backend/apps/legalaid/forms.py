from django import forms

from legalaid.models import CaseLog, CaseLogType


class OutcomeForm(forms.Form):
    outcome_code = forms.ModelChoiceField(
        queryset=CaseLogType.objects, to_field_name='code', empty_label=None
    )
    outcome_notes = forms.CharField(required=False, max_length=500)

    def __init__(self, *args, **kwargs):
        super(OutcomeForm, self).__init__(*args, **kwargs)

        self.fields['outcome_code'].queryset = self.get_outcome_code_queryset()

    def get_outcome_code_queryset(self):
        return CaseLogType.objects.filter(subtype='outcome')

    def save(self, case, user):
        data = self.cleaned_data

        CaseLog.objects.create(
            case=case, created_by=user,
            logtype=data['outcome_code'], notes=data['outcome_notes']
        )
