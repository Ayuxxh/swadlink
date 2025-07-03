from django.urls import path
from . import views


app_name = 'accounts'



urlpatterns = [
    path('login/', views.CafeLoginView.as_view(), name='login'),
    path('logout/', views.CafeLogoutView.as_view(), name='logout'),
]
