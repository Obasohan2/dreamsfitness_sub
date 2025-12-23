from django import forms
from django_summernote.widgets import SummernoteWidget
from .widgets import CustomClearableFileInput
from .models import BlogPost, Comment


class AddPostForm(forms.ModelForm):
    """
    Form for adding a blog post
    """
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'body', 'image']
        widgets = {
            'body': SummernoteWidget(),
        }

    image = forms.ImageField(
        label='Image',
        required=False,
        widget=CustomClearableFileInput
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'border-black rounded-0'


class PostForm(forms.ModelForm):
    """
    Form for editing a blog post
    """
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'body', 'image']
        widgets = {
            'body': SummernoteWidget(),
        }

    image = forms.ImageField(
        label='Image',
        required=False,
        widget=CustomClearableFileInput
    )


class CommentForm(forms.ModelForm):
    """
    Form for blog comments
    """
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
        }
