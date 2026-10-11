from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.urls import reverse

from books.models import Order, OrderItem
from tests.factories import BookFactory, CategoryFactory, OrderFactory


@pytest.mark.django_db
class TestBookPages:

    def test_book_list_page(self, client):
        response = client.get(reverse('books:book_list'))
        assert response.status_code == 200

    def test_book_list_displays_book(self, client):
        book = BookFactory(title='Integration Test Book')

        response = client.get(reverse('books:book_list'))

        assert response.status_code == 200
        assert 'Integration Test Book' in response.content.decode()

    def test_book_list_filter_by_category(self, client):
        category = CategoryFactory()
        book = BookFactory(category=category)

        response = client.get(
            reverse('books:book_list'),
            {'category': category.id},
        )

        assert response.status_code == 200
        assert book in response.context['books']

    def test_book_detail_page(self, client):
        book = BookFactory()

        response = client.get(
            reverse('books:book_detail', args=[book.id])
        )

        assert response.status_code == 200
        assert response.context['book'] == book


@pytest.mark.django_db
class TestCartFlow:

    def test_cart_page(self, client):
        response = client.get(reverse('books:cart_detail'))
        assert response.status_code == 200

    def test_add_book_to_cart(self, client):
        book = BookFactory()

        response = client.get(
            reverse('books:cart_add', args=[book.id])
        )

        assert response.status_code == 302

        session = client.session
        assert str(book.id) in session['cart']

    def test_remove_book_from_cart(self, client):
        book = BookFactory()

        client.get(reverse('books:cart_add', args=[book.id]))

        response = client.get(
            reverse('books:cart_remove', args=[book.id])
        )

        assert response.status_code == 302
        assert str(book.id) not in client.session['cart']

    def test_clear_cart(self, client):
        book = BookFactory()

        client.get(reverse('books:cart_add', args=[book.id]))

        response = client.get(reverse('books:cart_clear'))

        assert response.status_code == 302
        assert client.session.get('cart') in (None, {})


@pytest.mark.django_db
class TestOrderFlow:

    @patch('books.views.send_mail')
    def test_create_order(self, mock_send_mail, client):
        book = BookFactory()

        client.get(reverse('books:cart_add', args=[book.id]))

        response = client.post(
            reverse('books:order_create'),
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@example.com',
                'address': 'Test Street 1',
            },
        )

        assert response.status_code == 200
        assert Order.objects.count() == 1
        assert OrderItem.objects.count() == 1

    @patch('books.views.send_mail')
    def test_order_sends_email(self, mock_send_mail, client):
        book = BookFactory()

        client.get(reverse('books:cart_add', args=[book.id]))

        client.post(
            reverse('books:order_create'),
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@example.com',
                'address': 'Test Street 1',
            },
        )

        mock_send_mail.assert_called_once()

    @patch('books.views.send_mail')
    def test_cart_cleared_after_order(self, mock_send_mail, client):
        book = BookFactory()

        client.get(reverse('books:cart_add', args=[book.id]))

        client.post(
            reverse('books:order_create'),
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@example.com',
                'address': 'Test Street 1',
            },
        )

        assert client.session.get('cart') in (None, {})


@pytest.mark.django_db
class TestPaymentFlow:

    @patch('books.views.stripe.checkout.Session.create')
    def test_payment_process_redirects_to_stripe(
        self,
        mock_stripe_create,
        client,
    ):
        order = OrderFactory()

        mock_stripe_create.return_value = SimpleNamespace(
            url='https://example.com/checkout'
        )

        response = client.get(
            reverse('books:payment_process', args=[order.id])
        )

        assert response.status_code == 302
        assert response.url == 'https://example.com/checkout'
        mock_stripe_create.assert_called_once()

    @patch('books.views.stripe.checkout.Session.retrieve')
    def test_successful_payment_marks_order_paid(
        self,
        mock_retrieve,
        client,
    ):
        order = OrderFactory(paid=False)

        mock_retrieve.return_value = SimpleNamespace(
            payment_status='paid',
            metadata={'order_id': str(order.id)},
        )

        response = client.get(
            reverse('books:payment_success'),
            {'session_id': 'test_session'},
        )

        assert response.status_code == 200

        order.refresh_from_db()
        assert order.paid is True

    def test_payment_cancel_page(self, client):
        response = client.get(reverse('books:payment_cancel'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestAsyncViews:

    def test_async_book_count(self, client):
        BookFactory.create_batch(3)

        response = client.get(reverse('books:async_book_count'))

        assert response.status_code == 200
        assert response.context['count'] == 3