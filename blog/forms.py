from django import forms
from django_summernote.widgets import SummernoteWidget

from .models import BlogPost, Comment, Category
from .widgets import CustomClearableFileInput


# ====================================================
# BASE BLOG POST FORM
# ====================================================
class BasePostForm(forms.ModelForm):
    """
    Base form shared by Add & Edit post forms
    """

    image = forms.ImageField(
        label="Image",
        required=False,
        widget=CustomClearableFileInput(),
    )

    class Meta:
        model = BlogPost
        fields = [
            "title",
            "category",
            "body",
            "image",
        ]
        labels = {
            "title": "",
            "category": "Category",
            "body": "",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply consistent styling (exclude custom file widget)
        for name, field in self.fields.items():
            if name != "image":
                field.widget.attrs.setdefault(
                    "class",
                    "form-control border-black rounded-0"
                )

        # Category dropdown
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "Select category"


# ====================================================
# ADD POST FORM
# ====================================================
class AddPostForm(BasePostForm):
    """
    Form for creating a new blog post
    """

    class Meta(BasePostForm.Meta):
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Post title",
                }
            ),
            "body": SummernoteWidget(
                attrs={
                    "placeholder": "Share your update...",
                }
            ),
        }


# ====================================================
# EDIT POST FORM
# ====================================================
class PostForm(BasePostForm):
    """
    Form for editing an existing blog post
    """

    class Meta(BasePostForm.Meta):
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Post title",
                }
            ),
            "body": SummernoteWidget(
                attrs={
                    "placeholder": "Update your post content...",
                }
            ),
        }


# ====================================================
# COMMENT FORM (Used for Add/Edit)
# ====================================================
class CommentForm(forms.ModelForm):
    """
    Form used to create or edit a comment
    """

    class Meta:
        model = Comment
        fields = ["body"]
        labels = {
            "body": "",
        }
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "form-control rounded-0",
                    "rows": 3,
                    "placeholder": "Add a comment...",
                }
            ),
        }
