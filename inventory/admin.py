from django.contrib import admin
from .models import Category, Product, StockEntry, Sale


# 1. Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    list_filter = ("parent",)


# 2. Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "buying_price", "selling_price", "quantity", "reorder_level")
    search_fields = ("name",)
    list_filter = ("category",)
    ordering = ("name",)


# 3. StockEntry
@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "buying_price", "date_added", "added_by")
    search_fields = ("product__name",)
    list_filter = ("date_added", "added_by")
    ordering = ("-date_added",)


# 4. Sale
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "product", "quantity", "selling_price",
        "date_sold", "sold_by", "payment_status",
        "total_sale_value", "total_profit",
    )
    search_fields = ("product__name", "sold_by__username")
    list_filter = ("date_sold", "sold_by", "payment_status")
    ordering = ("-date_sold",)
