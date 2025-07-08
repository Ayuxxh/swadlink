from django.db import models

from cafes.models import Cafe 
from django.utils import timezone
from accounts.models import CustomUser
from customer.models import GlobalCustomerDB
from menu.models import Menu

from django.utils.timesince import timesince
from django.utils.timezone import now


from decimal import Decimal



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
        

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

