from django import forms
from .models import Product, StockEntry, Sale

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "reorder_level"]


class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockEntry
        fields = ["product", "quantity", "buying_price", "selling_price"]


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["product", "quantity", "selling_price"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "placeholder": "Enter quantity",
            }),
            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.01",
                "placeholder": "Enter selling price",
            }),
        }
