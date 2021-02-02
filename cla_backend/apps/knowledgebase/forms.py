from django import forms
from knowledgebase.utils.csv_user_import import KnowledgebaseCSVImporter


class KnowledgebaseCsvUploadForm(forms.Form):
    csv_file = forms.FileField(required=True)

    def clean(self):
        cleaned_data = super(KnowledgebaseCsvUploadForm, self).clean()
        importer = KnowledgebaseCSVImporter(cleaned_data["csv_file"])
        try:
            importer.parse()
        except Exception as e:
            raise forms.ValidationError(e.message)

    def process(self):
        pass
