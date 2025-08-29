from django.db import models
from django.core.exceptions import ValidationError
import math


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE,
        null=True, blank=True, related_name="subcategories"
    )

    def __str__(self):
        return f"{self.parent} -> {self.name}" if self.parent else self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name

    @property
    def stock_value(self):
        return self.buying_price * self.quantity

    @property
    def profit_margin(self):
        return self.selling_price - self.buying_price

    def needs_restock(self):
        return self.quantity <= self.reorder_level


class StockEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_entries")
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} {self.product.name} added on {self.date_added.date()}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            # old values
            old_qty = self.product.quantity
            old_cost = self.product.buying_price
            old_total = old_qty * old_cost

            # new values
            new_qty = self.quantity
            new_cost = self.buying_price
            new_total = new_qty * new_cost

            # update product qty
            total_qty = old_qty + new_qty
            if total_qty > 0:
                avg_cost = (old_total + new_total) / total_qty
            else:
                avg_cost = new_cost  # fallback

            # round up to nearest tens
            avg_cost = math.ceil(avg_cost / 10) * 10

            self.product.quantity = total_qty
            self.product.buying_price = avg_cost
            self.product.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Stock Entries"


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales")
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_sold = models.DateTimeField(auto_now_add=True)
    sold_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[("Paid", "Paid"), ("Credit", "Credit")],
        default="Paid"
    )

    def clean(self):
        if self.quantity > self.product.quantity:
            raise ValidationError(
                f"Not enough stock for {self.product.name}. "
                f"Available: {self.product.quantity}, Requested: {self.quantity}"
            )

    def save(self, *args, **kwargs):
        self.clean()
        if self.pk is None:  
            self.product.quantity -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)

    @property
    def total_sale_value(self):
        return self.quantity * self.selling_price

    @property
    def total_profit(self):
        return (self.selling_price - self.product.buying_price) * self.quantity
