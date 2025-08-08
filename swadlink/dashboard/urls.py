from django.urls import path, include

from . import views


app_name = 'dashboard'



urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('view-orders/', views.view_orders, name='view_order'),
    path('reports/', views.download_reports, name='reports'),
    path('edit-menu/', views.upload_menu, name='edit_menu'),
    
    path('employee/kot', views.kot, name='kot'),
    path('employee/kot/data/', views.kot_data, name='kot_data'),
    path('employee/kot/mark-served/<int:order_id>/', views.mark_order_served, name='kot_mark_served'),

    path('employee/', views.employee    , name='employee_dashboard'),
    path('employee/data', views.employee_live_orders    , name='employee_live_orders'),
    path('employee/order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('employee/order/close/<int:order_id>/', views.close_order, name='close_order'),
    path('employee/order/update/<int:order_id>/', views.close_order, name='update_order'),



]
