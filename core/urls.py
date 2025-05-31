from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, ContactViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'contacts', ContactViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]
