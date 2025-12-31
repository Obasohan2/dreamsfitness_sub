from django import forms
from django_summernote.widgets import SummernoteWidget

from .models import BlogPost, Comment
from .widgets import CustomClearableFileInput


class BasePostForm(forms.ModelForm):
    """
    Base form for creating and editing blog posts
    """

    image = forms.ImageField(
        label='Image',
        required=False,
        widget=CustomClearableFileInput()
    )

    class Meta:
        model = BlogPost
        fields = ['title', 'body', 'image']
        labels = {
            'title': '',
            'body': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name != 'image':
                field.widget.attrs.setdefault(
                    'class',
                    'form-control border-black rounded-0'
                )


class AddPostForm(BasePostForm):
    """
    Form for adding a blog post
    """

    class Meta(BasePostForm.Meta):
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': 'Post title',
                }
            ),
            'body': SummernoteWidget(
                attrs={
                    'placeholder': 'Write your post content here...',
                }
            ),
        }


class PostForm(BasePostForm):
    """
    Form for editing a blog post
    """

    class Meta(BasePostForm.Meta):
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': 'Post title',
                }
            ),
            'body': SummernoteWidget(
                attrs={
                    'placeholder': 'Update your post content...',
                }
            ),
        }


class CommentForm(forms.ModelForm):
    """
    Form for blog comments (authenticated users)
    """

    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Add a comment...',
                }
            ),
        }
