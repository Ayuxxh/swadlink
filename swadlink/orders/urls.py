from django.urls import path, include

from . import views


app_name = 'orders'




urlpatterns = [
    path('get-customer-details/', views.get_customer_details, name='create_orderget_customer_details'),
    path('select-items/', views.select_items, name='create_order.select_items'),
    path('summary/', views.summmary, name='create_order.order_summary'),
    path('update-items/', views.get_customer_details, name='create_order.update_items'),
    

]
