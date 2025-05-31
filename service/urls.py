from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, TypeViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'types', TypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]