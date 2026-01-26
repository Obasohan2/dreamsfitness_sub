from django import forms
from .models import Product, Category, Review
from .widgets import CustomClearableFileInput


class ProductForm(forms.ModelForm):
    images = forms.ImageField(
        label="Image",
        required=False,
        widget=CustomClearableFileInput,
    )

    class Meta:
        model = Product
        exclude = ("slug",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = Category.objects.all()

        for field in self.fields.values():
            field.widget.attrs["class"] = "border-black rounded-0"


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]
        widgets = {
            "rating": forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            "title": forms.TextInput(attrs={"placeholder": "Review title"}),
            "comment": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Write your review here...",
            }),
        }
