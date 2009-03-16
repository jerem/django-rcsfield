from django import forms
from rcs.wiki.models import WikiAttachment

class UploadForm(forms.ModelForm):
    class Meta:
        model = WikiAttachment
        fields = ('file',)
