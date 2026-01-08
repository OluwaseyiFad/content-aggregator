from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit, HTML
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from bleach import clean
from django.utils.safestring import mark_safe

from .models import MedicalImagingArticle, ArticleComment, ArticleImage

ALLOWED_TAGS = ['p', 'i', 'strong', 'em', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'code', 'pre']


class MedicalImagingArticleForm(forms.ModelForm):
    """Form for creating/editing medical imaging articles"""

    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = MedicalImagingArticle
        fields = ['title', 'summary', 'body', 'featured_image', 'primary_topic', 'meta_description']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'meta_description': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'title',
            'summary',
            'body',
            Div(
                Div('featured_image', css_class='col-md-6'),
                Div('primary_topic', css_class='col-md-6'),
                css_class='row'
            ),
            'meta_description',
            Submit('submit', 'Save Article', css_class='btn btn-primary mt-4')
        )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise forms.ValidationError('Title must be at least 10 characters long.')
        sanitized_title = clean(title, tags=[], strip=True)
        return sanitized_title

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if '<script>' in body.lower():
            raise forms.ValidationError("Content cannot contain script tags.")
        return mark_safe(body)

    def clean_summary(self):
        summary = self.cleaned_data.get('summary')
        sanitized_summary = clean(summary, tags=ALLOWED_TAGS, strip=True)
        return sanitized_summary


class ArticleCommentForm(forms.ModelForm):
    """Form for article comments"""

    class Meta:
        model = ArticleComment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts on this article...',
                'rows': 4
            })
        }

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if '<script>' in body.lower():
            raise forms.ValidationError("Comment cannot contain script tags.")
        sanitized_body = clean(body, tags=ALLOWED_TAGS, strip=True)
        return sanitized_body


class ArticleImageForm(forms.ModelForm):
    """Form for uploading article images"""

    class Meta:
        model = ArticleImage
        fields = ['image', 'caption', 'alt_text']
        widgets = {
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
        }
