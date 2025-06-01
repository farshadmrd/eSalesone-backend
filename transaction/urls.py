from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, BasketViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'baskets', BasketViewSet)

urlpatterns = router.urls
