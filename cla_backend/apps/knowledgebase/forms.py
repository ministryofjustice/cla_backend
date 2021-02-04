from django import forms
from knowledgebase.utils.csv_user_import import KnowledgebaseCSVImporter


class KnowledgebaseCSVUploadForm(forms.Form):
    csv_file = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super(KnowledgebaseCSVUploadForm, self).__init__(*args, **kwargs)
        self.rows = []

    @staticmethod
    def _raise_validation_errors(errors):
        validation_errors = []
        for error in errors:
            validation_errors.append(forms.ValidationError(error))
        raise forms.ValidationError(validation_errors)

    def clean(self):
        cleaned_data = super(KnowledgebaseCSVUploadForm, self).clean()
        self.rows, errors = KnowledgebaseCSVImporter.parse(cleaned_data["csv_file"])
        if errors:
            self._raise_validation_errors(errors)

    def save(self):
        KnowledgebaseCSVImporter.save(self.rows)
