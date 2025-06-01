from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, TypeViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'types', TypeViewSet, basename='type')

urlpatterns = [
    path('', include(router.urls)),
]