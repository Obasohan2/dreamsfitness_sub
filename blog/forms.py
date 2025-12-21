from django import forms
from .models import BlogPost
from django_summernote.widgets import SummernoteWidget


class PostForm(forms.ModelForm):
    """
    Form for editing a blog post
    """
    class Meta:
        model = BlogPost
        fields = [
            'title',
            'slug',
            'body',
            'image',
        ]
    image = forms.ImageField(
        label='Image', required=False)


class AddPostForm(forms.ModelForm):
    """
    Form for adding a blog post
    """
    class Meta:
        model = BlogPost
        widgets = {
            'body': SummernoteWidget()
        }

        fields = [
            'title',
            'slug',
            'body',
            'image',
        ]
    image = forms.ImageField(
        label='Image', required=False),

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'