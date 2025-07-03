from django.db import models
from cafes.models import Cafe 
from django.utils import timezone
from accounts.models import CustomUser



class Menu(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='menu')

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_veg = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.cafe.name}"




class GlobalCustomerDB(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)  # Unique mobile number
    
    visit_count = models.PositiveIntegerField(default=0)
    last_visit = models.DateTimeField(default=timezone.now)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def update_visit(self, amount_spent):
        """Call this when a new order is placed by the customer"""
        self.visit_count += 1
        self.last_visit = timezone.now()
        self.total_spent += amount_spent
        self.save()



class Table(models.Model):
    pass

class Order(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(GlobalCustomerDB, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

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

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"


class CafeCustomerDB(models.Model):
    phone = models.CharField(max_length=15)  
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='cafedb')

    def __str__(self):
        return f" ({self.phone}) - {self.cafe.name}"
    

    
    class Meta:
        unique_together = ('phone', 'cafe')  # Ensures same number can register with multiple cafes, but uniquely per cafe
