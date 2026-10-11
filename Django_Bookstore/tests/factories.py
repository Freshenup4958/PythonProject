import factory
from decimal import Decimal
from factory.django import DjangoModelFactory

from books.models import Category, Book, Order, OrderItem


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.Sequence(lambda n: f'category-{n}')


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    category = factory.SubFactory(CategoryFactory)
    title = factory.Sequence(lambda n: f'Book {n}')
    author = factory.Faker('name')
    price = Decimal('100.00')
    description = factory.Faker('sentence')
    stock = 10


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    address = factory.Faker('address')
    paid = False


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    book = factory.SubFactory(BookFactory)
    price = Decimal('100.00')
    quantity = 1