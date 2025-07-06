from django.db import models
from cafes.models import Cafe 
from django.utils import timezone




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




class CafeCustomerDB(models.Model):
    phone = models.CharField(max_length=15)  
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='cafe')

    def __str__(self):
        return f" ({self.phone}) - {self.cafe.name}"
    

    
    class Meta:
        unique_together = ('phone', 'cafe')  # Ensures same number can register with multiple cafes, but uniquely per cafe
