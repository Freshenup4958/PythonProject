
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    CategoryViewSet,
    CartViewSet,
    OrderViewSet,
)


router = DefaultRouter()

router.register('books', BookViewSet, basename='book')
router.register('categories', CategoryViewSet, basename='category')
router.register('cart', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
