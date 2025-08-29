import math

from decimal import Decimal

from django.db import models, transaction
from django.core.exceptions import ValidationError


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

    buying_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} {self.product.name} added on {self.date_added.date()}"
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            old_qty = self.product.quantity
            old_cost = self.product.buying_price
            old_sell = self.product.selling_price

            # Totals
            old_total_cost = old_qty * old_cost
            old_total_sell = old_qty * old_sell

            new_qty = self.quantity
            new_cost = self.buying_price
            new_sell = self.selling_price

            new_total_cost = new_qty * new_cost
            new_total_sell = new_qty * new_sell

            total_qty = old_qty + new_qty

            if total_qty > 0:
                avg_cost = (old_total_cost + new_total_cost) / total_qty
                avg_sell = (old_total_sell + new_total_sell) / total_qty
            else:
                avg_cost = new_cost
                avg_sell = new_sell

            # Round cost up to nearest 10
            avg_cost = Decimal(math.ceil(avg_cost / 10) * 10)

            # Update product
            self.product.quantity = total_qty
            self.product.buying_price = avg_cost
            self.product.selling_price = avg_sell
            self.product.save()

        super().save(*args, **kwargs)


    class Meta:
        verbose_name_plural = "Stock Entries"


class Sale(models.Model):
    PAYMENT_CHOICES = [
        ("Paid", "Paid"),
        ("Credit", "Credit"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="sales"
    )
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price_at_sale = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False
    )  # historical buying price snapshot

    date_sold = models.DateTimeField(auto_now_add=True)
    sold_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default="Paid"
    )

    class Meta:
        ordering = ["-date_sold"]
        verbose_name = "Sale"
        verbose_name_plural = "Sales"

    def __str__(self):
        return f"Sale of {self.product.name} ({self.quantity}) by {self.sold_by or 'Unknown'}"

    def clean(self):
        """Validations before saving."""
        if self.pk is None:  # only on creation
            if self.quantity > self.product.quantity:
                raise ValidationError(
                    f"Not enough stock for {self.product.name}. "
                    f"Available: {self.product.quantity}, Requested: {self.quantity}"
                )

            # Validate selling price is not below product cost
            if self.selling_price < self.product.buying_price:
                raise ValidationError(
                    f"Selling price ({self.selling_price}) cannot be lower "
                    f"than current cost price ({self.product.buying_price})"
                )

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Save sale:
        - Validate stock & pricing
        - Reduce stock atomically
        - Store cost price snapshot
        """
        is_new = self.pk is None
        self.clean()

        if is_new:
            # Lock product row to avoid race conditions
            product = Product.objects.select_for_update().get(pk=self.product.pk)

            if self.quantity > product.quantity:
                raise ValidationError(
                    f"Stock changed! Available: {product.quantity}, Requested: {self.quantity}"
                )

            # Record product cost price at sale time
            self.cost_price_at_sale = product.buying_price

            # Deduct stock
            product.quantity -= self.quantity
            product.save()

        super().save(*args, **kwargs)

    @property
    def total_sale_value(self) -> Decimal:
        """Total revenue from this sale."""
        return self.quantity * self.selling_price

    @property
    def total_profit(self) -> Decimal:
        """Profit made from this sale, based on cost at sale time."""
        return (self.selling_price - self.cost_price_at_sale) * self.quantity
