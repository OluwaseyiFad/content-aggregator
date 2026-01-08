from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from bleach import clean
from django.utils.safestring import mark_safe

from .models import BlogPost, ImageGallery, GalleryImage, ProgressBoard, ProgressColumn, ProgressCard, BlogComment

ALLOWED_TAGS = ['p', 'i', 'strong', 'em', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'code', 'pre', 'img']


class BlogPostForm(forms.ModelForm):
    """Form for creating/editing blog posts"""

    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = BlogPost
        fields = ['title', 'excerpt', 'body', 'featured_image']
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'title',
            'excerpt',
            'body',
            'featured_image',
            Submit('submit', 'Save Post', css_class='btn btn-primary mt-4')
        )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return clean(title, tags=[], strip=True)

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if '<script>' in body.lower():
            raise forms.ValidationError("Content cannot contain script tags.")
        return mark_safe(body)


class ProgressBoardForm(forms.ModelForm):
    """Form for creating/editing progress boards"""

    class Meta:
        model = ProgressBoard
        fields = ['title', 'description', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class ProgressColumnForm(forms.ModelForm):
    """Form for creating/editing progress columns"""

    class Meta:
        model = ProgressColumn
        fields = ['title', 'color']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
        }


class ProgressCardForm(forms.ModelForm):
    """Form for creating/editing progress cards"""

    class Meta:
        model = ProgressCard
        fields = ['title', 'description', 'due_date', 'completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class GalleryImageForm(forms.ModelForm):
    """Form for uploading gallery images"""

    class Meta:
        model = GalleryImage
        fields = ['image', 'caption', 'alt_text']
        widgets = {
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BlogCommentForm(forms.ModelForm):
    """Form for blog comments"""

    class Meta:
        model = BlogComment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts...',
                'rows': 4
            })
        }

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if '<script>' in body.lower():
            raise forms.ValidationError("Comment cannot contain script tags.")
        return clean(body, tags=ALLOWED_TAGS, strip=True)
