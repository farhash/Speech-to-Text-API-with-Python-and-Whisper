from django import forms
from stt.models import upload_audio

class FileForm(forms.ModelForm):
    class Meta:
        model = upload_audio
        fields = ("audio",)

