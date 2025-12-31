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
        fields = ['title', 'body', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Post title',
            }),
            'body': SummernoteWidget(attrs={
                'placeholder': 'Write your post content here...',
            }),
        }
        labels = {
            'title': '',
            'body': '',
        }

    image = forms.ImageField(
        label='Image',
        required=False,
        widget=CustomClearableFileInput
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'form-control border-black rounded-0'
            )


class PostForm(forms.ModelForm):
    """
    Form for editing a blog post
    """
    class Meta:
        model = BlogPost
        fields = ['title', 'body', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Post title',
            }),
            'body': SummernoteWidget(attrs={
                'placeholder': 'Update your post content...',
            }),
        }
        labels = {
            'title': '',
            'body': '',
        }

    image = forms.ImageField(
        label='Image',
        required=False,
        widget=CustomClearableFileInput
    )


class CommentForm(forms.ModelForm):
    """
    Form for blog comments (authenticated users)
    """
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
        }
