from django import forms
from .models import Product, Category
from .widgets import CustomClearableFileInput

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
    
    images = forms.ImageField(label='Image', required=False, widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = Category.objects.all()
        self.fields["category"].choices = [
            (c.id, c.name) for c in categories
        ]

        for field in self.fields.values():
            field.widget.attrs["class"] = "border-black rounded-0"
