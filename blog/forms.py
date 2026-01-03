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
            "is_success_story",
            "body",
            "image",
        ]
        labels = {
            "title": "",
            "category": "Category",
            "is_success_story": "Mark as success story",
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
    Form for creating a new blog post.
    Success Story checkbox is visible to ALL users.
    Backend enforces subscriber-only rules.
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

    def __init__(self, *args, **kwargs):
        # Keep user available if you want messaging later
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Optional: helper text for clarity
        self.fields["is_success_story"].help_text = (
            "Optional. Subscriber-only feature. "
            "Free users’ selections may be ignored."
        )


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
# COMMENT FORM
# ====================================================
class CommentForm(forms.ModelForm):
    """
    Form for authenticated users to comment on posts
    """

    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "form-control rounded-0",
                    "rows": 3,
                    "placeholder": "Add a comment...",
                }
            ),
        }
