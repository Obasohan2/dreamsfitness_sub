from django import forms

from .models import BlogPost, Comment, Category
from .widgets import CustomClearableFileInput


# ====================================================
# BASE BLOG POST FORM
# ====================================================
class BasePostForm(forms.ModelForm):
    image = forms.ImageField(
        label="Image",
        required=False,
        widget=CustomClearableFileInput(),
    )

    body = forms.CharField(
        label="Body",
        widget=forms.Textarea(
            attrs={
                "class": "form-control border-black rounded-0",
                "rows": 12,
                "placeholder": "Write your post here...",
            }
        ),
    )

    class Meta:
        model = BlogPost
        fields = ["title", "category", "body", "image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name not in ("image", "body"):
                field.widget.attrs.setdefault(
                    "class", "form-control border-black rounded-0"
                )

        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "Select category"


# ====================================================
# ADD / EDIT POST FORMS
# ====================================================
class AddPostForm(BasePostForm):
    pass


class PostForm(BasePostForm):
    pass


# ====================================================
# COMMENT FORM
# ====================================================
class CommentForm(forms.ModelForm):
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
