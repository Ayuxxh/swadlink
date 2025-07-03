from django.contrib import admin

from .models import *

admin.site.register(Menu)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(GlobalCustomerDB)
admin.site.register(CafeCustomerDB)