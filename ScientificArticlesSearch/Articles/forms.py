from django import forms
from .models import UploadedArticle

class ArticleUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedArticle
        fields = ('file',)