from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, ContactViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'contacts', ContactViewSet, basename='contact')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/', include(router.urls)),
]
