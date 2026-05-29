from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'vehicles', VehicleViewSet)

# XATO SHU YERDA EDI: basename qo'shildi
router.register(r'orders', OrderViewSet, basename='order') 

router.register(r'locations', LocationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/', DashboardStatisticsView.as_view(), name='dashboard-statistics'), # Shu qator qo'shildi
]