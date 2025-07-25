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



]
