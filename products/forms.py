from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = Category.objects.all()
        self.fields["category"].choices = [
            (c.id, c.name) for c in categories
        ]

        for field in self.fields.values():
            field.widget.attrs["class"] = "border-black rounded-0"
