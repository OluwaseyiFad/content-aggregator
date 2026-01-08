from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from bleach import clean
from django.utils.safestring import mark_safe

from .models import Story, StoryChapter, StoryComment

ALLOWED_TAGS = ['p', 'i', 'strong', 'em', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'blockquote']


class StoryForm(forms.ModelForm):
    """Form for creating/editing stories"""

    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Story
        fields = ['title', 'summary', 'body', 'genre', 'cover_image']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'title',
            'summary',
            'genre',
            'body',
            'cover_image',
            Submit('submit', 'Save Story', css_class='btn btn-primary mt-4')
        )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters long.')
        return clean(title, tags=[], strip=True)

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if '<script>' in body.lower():
            raise forms.ValidationError("Story content cannot contain script tags.")
        return mark_safe(body)


class StoryChapterForm(forms.ModelForm):
    """Form for creating/editing story chapters"""

    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = StoryChapter
        fields = ['title', 'body']

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if '<script>' in body.lower():
            raise forms.ValidationError("Chapter content cannot contain script tags.")
        return mark_safe(body)


class StoryCommentForm(forms.ModelForm):
    """Form for story comments"""

    class Meta:
        model = StoryComment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts on this story...',
                'rows': 4
            })
        }

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if '<script>' in body.lower():
            raise forms.ValidationError("Comment cannot contain script tags.")
        return clean(body, tags=ALLOWED_TAGS, strip=True)
