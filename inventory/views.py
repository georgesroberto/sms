import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.shortcuts import render, redirect
from django.utils.timezone import now
from datetime import timedelta

from .models import Product, Sale, StockEntry
from .forms import ProductForm, StockEntryForm, SaleForm

from users.models import User


# Create your views here
@login_required
def admin_dashboard(request):
    today = now().date()

    # Total stock (sum of quantities)
    total_stock = Product.objects.aggregate(total=Sum("quantity"))["total"] or 0

    # Sales today
    sales_today = Sale.objects.filter(date_sold__date=today).count()

    # Low stock alerts (e.g., below 5 units)
    low_stock_count = Product.objects.filter(quantity__lt=5).count()

    # Shopkeepers (users who sold something or all users except admin?)
    shopkeepers_count = User.objects.filter(is_staff=False).count()

    # Sales trend (last 6 months)
    last_6_months = [(today.replace(day=1) - timedelta(days=30*i)) for i in range(5, -1, -1)]
    sales_labels = [d.strftime("%b") for d in last_6_months]
    sales_values = []
    for d in last_6_months:
        month_sales = (
            Sale.objects.filter(date_sold__month=d.month, date_sold__year=d.year)
            .aggregate(
                total=Sum(
                    ExpressionWrapper(F("quantity") * F("selling_price"), output_field=DecimalField())
                )
            )["total"] or 0
        )

        sales_values.append(float(month_sales))

    # Stock distribution (by category if Product has category field, else dummy)
    stock_distribution = (
        Product.objects.values("category__name")  # assuming category relation
        .annotate(total=Sum("quantity"))
    )
    stock_labels = [item["category__name"] for item in stock_distribution] or ["Uncategorized"]
    stock_values = [item["total"] for item in stock_distribution] or [0]
    
    context = {
        "total_stock": total_stock,
        "sales_today": sales_today,
        "low_stock_count": low_stock_count,
        "shopkeepers_count": shopkeepers_count,
        "sales_trend_labels": json.dumps(sales_labels),
        "sales_trend_values": json.dumps(sales_values),
        "stock_labels": json.dumps(stock_labels),
        "stock_values": json.dumps(stock_values),
    }
    return render(request, "admin/dashboard.html", context)


@login_required
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


@login_required
def sales_report(request):
    sales = Sale.objects.annotate(
        profit_margin=ExpressionWrapper(
            ((F("selling_price") - F("product__buying_price")) / F("selling_price")) * 100,
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    ).order_by("-date_sold")
    
    return render(request, "admin/sales_report.html", {"sales": sales})


@login_required
def vendor_dashboard(request):
    products = Product.objects.all()
    today = now().date()

    # Today's sales queryset
    todays_sales_qs = Sale.objects.filter(
        sold_by=request.user,
        date_sold__date=today
    )

    # Compute totals
    todays_sales_count = todays_sales_qs.count()
    todays_revenue = sum(float(s.total_sale_value) for s in todays_sales_qs) or 0

    # Weekly sales trend (ensure all values are floats)
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    daily_sales = []
    for day in last_7_days:
        sales_for_day = Sale.objects.filter(
            sold_by=request.user,
            date_sold__date=day
        )
        total_for_day = sum(float(s.total_sale_value) for s in sales_for_day) or 0
        daily_sales.append(total_for_day)

    return render(request, "vendor/index.html", {
        "products_count": products.count(),
        "todays_sales_count": todays_sales_count,
        "todays_revenue": todays_revenue,
        "sales_trend_labels": json.dumps([d.strftime("%a") for d in last_7_days]),
        "sales_trend_values": json.dumps(daily_sales),
    })


@login_required
def vendor_sales(request):
    products = Product.objects.all().order_by("name")
    sales = Sale.objects.filter(sold_by=request.user).order_by("-date_sold")
    total_sales_amount = sum(s.total_sale_value for s in sales) or 0

    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.sold_by = request.user
            try:
                sale.save()
                # Store last sale ID in messages
                messages.success(request, f"✅ Sale of {sale.product.name} recorded successfully!", extra_tags=f"highlight-{sale.id}")
                return redirect("inventory:vendor_sales")
            except Exception as e:
                messages.error(request, f"⚠️ {str(e)}")
                return redirect("inventory:vendor_sales")
        else:
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_list.append(f"{field.capitalize()}: {error}")
            for error in form.non_field_errors():
                error_list.append(error)

            messages.error(
                request,
                "⚠️ Could not record sale: " + " | ".join(error_list)
                if error_list else "⚠️ Invalid form submission."
            )
            return redirect("inventory:vendor_sales")

    else:
        form = SaleForm()

    product_prices = {p.id: str(p.selling_price) for p in products}

    return render(request, "vendor/sales.html", {
        "products": products,
        "sales": sales,
        "total_sales_amount": total_sales_amount,
        "sale_form": form,
        "product_prices": product_prices,
    })
