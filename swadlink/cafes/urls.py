from django.urls import path, include
from . import views

urlpatterns = [
    path('<slug:slug>/', include('accounts.urls')),
    path('<slug:slug>/dashboard/', include('dashboard.urls'))
]