from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'services', views.ServiceViewSet)
router.register(r'types', views.TypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('basket/', views.SessionBasketView.as_view(), name='session-basket'),
    path('basket/clear/', views.clear_basket, name='clear-basket'),
]