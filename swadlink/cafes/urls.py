from django.urls import path, include
from . import views

urlpatterns = [
    path('<slug:slug>/', include('accounts.urls')),
    path('<slug:slug>/dashboard/', include('dashboard.urls')),
    path('<slug:slug>/dashboard/employee/orders/', include('orders.urls', namespace='orders')),
    path('<slug:slug>/menu', include('menu.urls', namespace='menu')),
]