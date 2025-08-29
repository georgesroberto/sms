from django import forms
from .models import Product, StockEntry

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "buying_price", "selling_price", "quantity", "reorder_level"]

class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockEntry
        fields = ["product", "quantity", "buying_price"]
