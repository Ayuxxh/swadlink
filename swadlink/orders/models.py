from django.db import models

from cafes.models import Cafe 
from django.utils import timezone
from accounts.models import CustomUser
from customer.models import GlobalCustomerDB
from menu.models import Menu

from django.utils.timesince import timesince
from django.utils.timezone import now


from decimal import Decimal

from django.utils.timezone import localtime, make_aware
from datetime import timedelta, time
from django.db.models import Max
from pytz import timezone as pytz_timezone
from datetime import datetime as dt

import re

def generate_order_code(cafe, created_at):
    IST = pytz_timezone('Asia/Kolkata')
    created_local = localtime(created_at, timezone=IST)

    # Adjust the date to reflect the 4 AM café day start
    if created_local.time() < time(4, 0):
        cafe_day = (created_local - timedelta(days=1)).date()
    else:
        cafe_day = created_local.date()

    day_str = cafe_day.strftime('%Y-%m-%d')
    cafe_slug = cafe.slug.upper()
    prefix = f"{cafe_slug}-{day_str}"

    # 4 AM to next 4 AM range
    start_of_day = make_aware(dt.combine(cafe_day, time(4, 0)), IST)
    end_of_day = start_of_day + timedelta(days=1)

    # Fetch only relevant order codes for the day
    order_codes = Order.objects.filter(
        cafe=cafe,
        created_at__range=(start_of_day, end_of_day),
        order_code__startswith=prefix
    ).values_list('order_code', flat=True)

    max_number = 0
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")

    for code in order_codes:
        match = pattern.match(code)
        if match:
            num = int(match.group(1))
            if num > max_number:
                max_number = num

    next_number = max_number + 1
    return f"{prefix}-{next_number:03d}"

class Table(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=10)  # could also be IntegerField
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.table_number} - {self.cafe.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('served', 'Served'),
    ]

    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(GlobalCustomerDB, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_code = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} at {self.cafe.name}"

    def is_active(self):
        return self.status == 'active'

    def is_completed(self):
        return self.status == 'completed'

    def cancel_order(self):
        self.status = 'cancelled'
        self.save()

    def mark_completed(self):
        self.status = 'completed'
        self.save()

    def kot_display(self):
        """Returns the current live KOT view of the order."""
        return {
            "Order ID": self.id,
            "Customer": self.customer.name,
            "Phone": self.customer.phone_number,
            "Table": self.table.table_number if self.table else "No table",
            "Items": [
                {
                    "name": item.menu_item.name,
                    "quantity": item.quantity
                } for item in self.items.all()
            ],
            "Created At": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "Status": self.status,
            "Cafe": self.cafe.name
        }
    

    @property
    def total_amount(self):
        return sum(
            Decimal(item.quantity) * item.menu_item.price
            for item in self.items.select_related('menu_item').all()
        )
    

    @property
    def estimated_profit(self):
        return self.total_amount - self.real_cost
        
    @property
    def real_cost(self):
        return sum(
            Decimal(item.quantity) * (item.menu_item.cost or Decimal('0'))
            for item in self.items.select_related('menu_item').all()
        )
    
    @classmethod
    def get_average_order_value(cls, queryset):
        count = queryset.count()
        if count == 0:
            return Decimal('0.00')
        total = sum(order.total_amount for order in queryset)
        return total / Decimal(count)
    
    @property
    def time_ago(self):
        return timesince(self.created_at, now()) + " ago"
    

    def merge_items(self, new_items):
        """
        Merge new items into this order instance:
        - Increase quantity if item exists.
        - Create new item if it doesn't.
        """
        from menu.models import Menu  # local import to avoid circular issues

        for item in new_items:
            menu_item_id = item.get("menu_item_id")
            quantity = item.get("quantity", 1)

            if not menu_item_id or quantity <= 0:
                continue

            try:
                menu_item = Menu.objects.get(pk=menu_item_id)
            except Menu.DoesNotExist:
                continue  # or raise error if you want strict enforcement

            order_item, created = self.items.get_or_create(
                menu_item=menu_item,
                defaults={'quantity': quantity}
            )

            if not created:
                order_item.quantity += quantity
                order_item.save()

    def save(self, *args, **kwargs):
        if not self.pk and not self.order_code:
            self.created_at = self.created_at or timezone.now()
            self.order_code = generate_order_code(self.cafe, self.created_at)
        super().save(*args, **kwargs)

            

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

