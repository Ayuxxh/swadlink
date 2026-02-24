from django.urls import path, include
from . import views
from .views import keep_alive  , keep_alive_render

urlpatterns = [
    path('<slug:slug>/', include('accounts.urls')),
    path('<slug:slug>/dashboard/', include('dashboard.urls')),
    path('<slug:slug>/dashboard/employee/orders/', include('orders.urls', namespace='orders')),
    path('<slug:slug>/menu', include('menu.urls', namespace='menu')),
    path('', views.landing),
    path('manifest-<slug:slug>.json', views.generate_manifest, name='cafe_manifest'),
    path("ping-db/", keep_alive),
    path("ping-render/", keep_alive_render),
]