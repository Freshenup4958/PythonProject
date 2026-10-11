from decimal import Decimal

import pytest

from books.cart import Cart
from books.forms import OrderCreateForm
from tests.factories import (
    BookFactory,
    CategoryFactory,
    OrderFactory,
    OrderItemFactory,
)


@pytest.mark.django_db
class TestCategoryModel:

    def test_category_creation(self):
        category = CategoryFactory()
        assert category.pk is not None

    def test_category_str(self):
        category = CategoryFactory(name='Fiction')
        assert str(category) == 'Fiction'

    def test_category_slug(self):
        category = CategoryFactory(slug='fiction')
        assert category.slug == 'fiction'


@pytest.mark.django_db
class TestBookModel:

    def test_book_creation(self):
        book = BookFactory()
        assert book.pk is not None

    def test_book_str(self):
        book = BookFactory(title='Django Book')
        assert str(book) == 'Django Book'

    def test_book_default_stock(self):
        book = BookFactory(stock=10)
        assert book.stock == 10

    def test_book_price(self):
        book = BookFactory(price=Decimal('125.50'))
        assert book.price == Decimal('125.50')

    def test_book_has_category(self):
        category = CategoryFactory()
        book = BookFactory(category=category)
        assert book.category == category


@pytest.mark.django_db
class TestOrderModel:

    def test_order_creation(self):
        order = OrderFactory()
        assert order.pk is not None

    def test_order_default_paid(self):
        order = OrderFactory()
        assert order.paid is False

    def test_order_str(self):
        order = OrderFactory()
        assert str(order) == f'Order {order.id}'

    def test_order_total_cost(self):
        order = OrderFactory()

        OrderItemFactory(
            order=order,
            price='100.00',
            quantity=2,
        )

        OrderItemFactory(
            order=order,
            price='50.00',
            quantity=1,
        )

        assert order.get_total_cost() == Decimal('250.00')


@pytest.mark.django_db
class TestOrderItemModel:

    def test_order_item_creation(self):
        item = OrderItemFactory()
        assert item.pk is not None

    def test_order_item_cost(self):
        item = OrderItemFactory(
            price=Decimal('25.00'),
            quantity=4,
        )

        assert item.get_cost() == Decimal('100.00')

    def test_order_item_str(self):
        book = BookFactory(title='Test Book')

        item = OrderItemFactory(
            book=book,
            quantity=3,
        )

        assert str(item) == 'Test Book x 3'


@pytest.mark.django_db
class TestOrderCreateForm:

    def test_valid_order_form(self):
        form = OrderCreateForm(
            data={
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@example.com',
                'address': 'Test Street 1',
            }
        )

        assert form.is_valid()

    def test_form_requires_first_name(self):
        form = OrderCreateForm(
            data={
                'last_name': 'Smith',
                'email': 'john@example.com',
                'address': 'Test Street 1',
            }
        )

        assert not form.is_valid()
        assert 'first_name' in form.errors

    def test_form_requires_last_name(self):
        form = OrderCreateForm(
            data={
                'first_name': 'John',
                'email': 'john@example.com',
                'address': 'Test Street 1',
            }
        )

        assert not form.is_valid()
        assert 'last_name' in form.errors

    def test_form_rejects_invalid_email(self):
        form = OrderCreateForm(
            data={
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'not-an-email',
                'address': 'Test Street 1',
            }
        )

        assert not form.is_valid()
        assert 'email' in form.errors

    def test_form_requires_address(self):
        form = OrderCreateForm(
            data={
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@example.com',
            }
        )

        assert not form.is_valid()
        assert 'address' in form.errors