from django.db.models import F, ExpressionWrapper, DecimalField
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Product, Sale, StockEntry
from .forms import ProductForm, StockEntryForm

# Create your views here.
def stock_list(request):
    products = Product.objects.all().order_by("name")
    stock_entries = StockEntry.objects.select_related("product", "added_by").order_by("-date_added")

    # Handle create product
    if request.method == "POST" and "create_product" in request.POST:
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventory:stock")

    # Handle stock entry
    if request.method == "POST" and "add_stock" in request.POST:
        stock_form = StockEntryForm(request.POST)
        if stock_form.is_valid():
            stock_entry = stock_form.save(commit=False)
            stock_entry.added_by = request.user        
            stock_entry.save()
            return redirect("inventory:stock")


    context = {
        "products": products,
        "stock_entries": stock_entries,
        "form": ProductForm(),
        "stock_form": StockEntryForm()
    }
    return render(request, "admin/stock.html", context)


def sales_report(request):
    sales = Sale.objects.annotate(
        profit_margin=ExpressionWrapper(
            ((F("selling_price") - F("product__buying_price")) / F("selling_price")) * 100,
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    ).order_by("-date_sold")
    
    return render(request, "admin/sales_report.html", {"sales": sales})
