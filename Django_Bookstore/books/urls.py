from django.urls import path
from . import views
from .views import (
    BookListView,
    BookDetailView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView,
    cart_detail,
    cart_add,
    cart_remove,
    cart_clear,
    order_create,
    payment_process,
    payment_success,
    payment_cancel,
)

app_name = 'books'

urlpatterns = [
    path('', BookListView.as_view(), name='book_list'),
    path('book/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('book/add/', BookCreateView.as_view(), name='book_create'),
    path('book/<int:pk>/edit/', BookUpdateView.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:book_id>/', cart_add, name='cart_add'),
    path('cart/remove/<int:book_id>/', cart_remove, name='cart_remove'),
    path('cart/clear/', cart_clear, name='cart_clear'),
    path('order/create/', order_create, name='order_create'),
    path('payment/process/<int:order_id>/',payment_process,name='payment_process'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/cancel/', payment_cancel, name='payment_cancel'),
    path('async/book-count/', views.async_book_count, name='async_book_count'),
    path('async/book/<int:book_id>/', views.async_book_detail, name='async_book_detail'),
    path('async/order-count/', views.async_order_count, name='async_order_count'),
]