
from rest_framework import permissions, viewsets

from books.models import Book, Category
from .serializers import BookSerializer, CategorySerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from books.cart import Cart
from .serializers import CartAddSerializer
from books.models import Order
from .serializers import OrderSerializer
from .permissions import IsOwnerOrReadOnly
from django.db import transaction
from rest_framework.exceptions import ValidationError

from books.models import OrderItem
from .serializers import OrderCreateSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('category').all()
    serializer_class = BookSerializer

    filterset_fields = ['category', 'author']
    search_fields = ['title', 'author', 'description']
    ordering_fields = ['price', 'title', 'stock', 'id']
    ordering = ['id']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filterset_fields = ['slug']
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    ordering = ['id']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        cart = Cart(request)

        items = []
        for item in cart:
            book = item['book']
            items.append({
                'book_id': book.id,
                'title': book.title,
                'quantity': item['quantity'],
                'price': str(item['price']),
                'total_price': str(item['total_price']),
            })

        return Response({
            'items': items,
            'total_quantity': len(cart),
            'total_price': str(cart.get_total_price()),
        })

    @action(detail=False, methods=['post'])
    def add(self, request):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book = serializer.validated_data['book']
        quantity = serializer.validated_data['quantity']
        override_quantity = serializer.validated_data['override_quantity']

        cart = Cart(request)
        cart.add(
            book=book,
            quantity=quantity,
            override_quantity=override_quantity,
        )

        return Response(
            {'message': 'Book added to cart'},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=['delete'],
        url_path=r'remove/(?P<book_id>[0-9]+)',
    )
    def remove(self, request, book_id=None):
        book = get_object_or_404(Book, pk=book_id)
        cart = Cart(request)
        cart.remove(book)

        return Response(
            {'message': 'Book removed from cart'},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = Cart(request)

        if cart.cart:
            cart.clear()

        return Response(
            {'message': 'Cart cleared'},
            status=status.HTTP_200_OK,
        )


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly,
    ]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related('items__book__category')
            .order_by('-created')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = Cart(request)

        if not cart.cart:
            raise ValidationError({
                'cart': 'Cart is empty.'
            })

        with transaction.atomic():
            book_ids = list(cart.cart.keys())

            books = Book.objects.select_for_update().filter(
                id__in=book_ids
            )
            books_by_id = {
                str(book.id): book for book in books
            }

            order_items = []

            for book_id, cart_item in cart.cart.items():
                book = books_by_id.get(book_id)
                quantity = cart_item['quantity']

                if book is None:
                    raise ValidationError({
                        'cart': f'Book {book_id} does not exist.'
                    })

                if quantity < 1 or book.stock < quantity:
                    raise ValidationError({
                        'cart': (
                            f'Not enough stock for "{book.title}".'
                        )
                    })

                order_items.append((book, quantity))

            order = serializer.save(user=request.user)

            for book, quantity in order_items:
                OrderItem.objects.create(
                    order=order,
                    book=book,
                    price=book.price,
                    quantity=quantity,
                )

                book.stock -= quantity
                book.save(update_fields=['stock'])

        cart.clear()

        response_serializer = OrderSerializer(
            order,
            context={'request': request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
