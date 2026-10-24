
from rest_framework import serializers

from books.models import Book, Category, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class BookSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(
        source='category',
        read_only=True
    )

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'price',
            'description',
            'stock',
            'category',
            'category_detail',
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    book_detail = BookSerializer(
        source='book',
        read_only=True
    )
    total_price = serializers.DecimalField(
        source='get_cost',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'book',
            'book_detail',
            'price',
            'quantity',
            'total_price',
        ]
        read_only_fields = ['price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True
    )
    total_cost = serializers.DecimalField(
        source='get_total_cost',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'address',
            'created',
            'paid',
            'items',
            'total_cost',
        ]
        read_only_fields = ['created', 'paid']

class CartItemSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    price = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )


class CartAddSerializer(serializers.Serializer):
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source='book'
    )
    quantity = serializers.IntegerField(
        min_value=1,
        default=1
    )
    override_quantity = serializers.BooleanField(
        default=False
    )


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'address',
        ]
