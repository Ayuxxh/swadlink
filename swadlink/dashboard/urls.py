from django.urls import path
from . import views


app_name = 'dashboard'



urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('view-orders/', views.view_orders, name='view_order'),
    path('reports/', views.download_reports, name='reports'),
    path('edit-menu/', views.upload_menu, name='menu_upload'),


]
