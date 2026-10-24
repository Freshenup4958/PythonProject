
import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from books.models import Book, Category, Order, OrderItem

from django.core.cache import cache
from django.test import override_settings



pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def category():
    return Category.objects.create(
        name='Programming',
        slug='programming',
    )


@pytest.fixture
def book(category):
    return Book.objects.create(
        category=category,
        title='Python Basics',
        author='Test Author',
        price='250.00',
        description='Learn Python',
        stock=10,
    )


@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        username='testuser',
        password='TestPass123!',
    )


@pytest.fixture
def admin_user():
    return get_user_model().objects.create_superuser(
        username='testadmin',
        email='admin@example.com',
        password='AdminPass123!',
    )


@pytest.fixture
def auth_client(user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(admin_user):
    api_client = APIClient()
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def order(user, book):
    order = Order.objects.create(
        user=user,
        first_name='Test',
        last_name='User',
        email='test@example.com',
        address='Test Street',
    )
    OrderItem.objects.create(
        order=order,
        book=book,
        price=book.price,
        quantity=2,
    )
    return order


def test_books_list_public(client, book):
    response = client.get('/api/books/')
    assert response.status_code == 200


def test_books_list_contains_book(client, book):
    response = client.get('/api/books/')
    assert response.data['results'][0]['title'] == 'Python Basics'


def test_book_detail(client, book):
    response = client.get(f'/api/books/{book.id}/')
    assert response.status_code == 200


def test_book_not_found(client):
    response = client.get('/api/books/999999/')
    assert response.status_code == 404


def test_book_search(client, book):
    response = client.get('/api/books/?search=Python')
    assert response.data['count'] == 1


def test_book_search_no_results(client, book):
    response = client.get('/api/books/?search=Nonexistent')
    assert response.data['count'] == 0


def test_book_filter_category(client, book, category):
    response = client.get(
        f'/api/books/?category={category.id}'
    )
    assert response.data['count'] == 1


def test_book_filter_author(client, book):
    response = client.get(
        '/api/books/?author=Test%20Author'
    )
    assert response.data['count'] == 1


def test_book_ordering_price(client, book):
    response = client.get('/api/books/?ordering=price')
    assert response.status_code == 200


def test_book_create_anonymous_forbidden(client, category):
    response = client.post(
        '/api/books/',
        {
            'category': category.id,
            'title': 'New Book',
            'author': 'Author',
            'price': '100.00',
            'stock': 5,
        },
    )
    assert response.status_code in (401, 403)


def test_book_create_admin(admin_client, category):
    response = admin_client.post(
        '/api/books/',
        {
            'category': category.id,
            'title': 'Admin Book',
            'author': 'Author',
            'price': '100.00',
            'stock': 5,
        },
    )
    assert response.status_code == 201


def test_book_delete_anonymous_forbidden(client, book):
    response = client.delete(f'/api/books/{book.id}/')
    assert response.status_code in (401, 403)


def test_categories_list_public(client, category):
    response = client.get('/api/categories/')
    assert response.status_code == 200


def test_category_detail(client, category):
    response = client.get(
        f'/api/categories/{category.id}/'
    )
    assert response.status_code == 200


def test_category_create_anonymous_forbidden(client):
    response = client.post(
        '/api/categories/',
        {
            'name': 'New Category',
            'slug': 'new-category',
        },
    )
    assert response.status_code in (401, 403)


def test_category_create_admin(admin_client):
    response = admin_client.post(
        '/api/categories/',
        {
            'name': 'Science',
            'slug': 'science',
        },
    )
    assert response.status_code == 201


def test_cart_empty(client):
    response = client.get('/api/cart/')
    assert response.status_code == 200
    assert response.data['total_quantity'] == 0


def test_cart_add_book(client, book):
    response = client.post(
        '/api/cart/add/',
        {
            'book_id': book.id,
            'quantity': 2,
            'override_quantity': False,
        },
    )
    assert response.status_code == 200


def test_cart_add_updates_quantity(client, book):
    for _ in range(2):
        client.post(
            '/api/cart/add/',
            {
                'book_id': book.id,
                'quantity': 2,
                'override_quantity': False,
            },
        )

    response = client.get('/api/cart/')
    assert response.data['total_quantity'] == 4


def test_cart_override_quantity(client, book):
    client.post(
        '/api/cart/add/',
        {
            'book_id': book.id,
            'quantity': 2,
            'override_quantity': False,
        },
    )

    client.post(
        '/api/cart/add/',
        {
            'book_id': book.id,
            'quantity': 1,
            'override_quantity': True,
        },
    )

    response = client.get('/api/cart/')
    assert response.data['total_quantity'] == 1


def test_cart_total_price(client, book):
    client.post(
        '/api/cart/add/',
        {
            'book_id': book.id,
            'quantity': 2,
            'override_quantity': False,
        },
    )

    response = client.get('/api/cart/')
    assert response.data['total_price'] == '500.00'


def test_cart_remove_book(client, book):
    client.post(
        '/api/cart/add/',
        {
            'book_id': book.id,
            'quantity': 1,
            'override_quantity': False,
        },
    )

    response = client.delete(
        f'/api/cart/remove/{book.id}/'
    )
    assert response.status_code == 200
    assert client.get('/api/cart/').data['total_quantity'] == 0


def test_cart_clear(client, book):
    client.post(
        '/api/cart/add/',
        {
            'book_id': book.id,
            'quantity': 1,
            'override_quantity': False,
        },
    )

    response = client.delete('/api/cart/clear/')
    assert response.status_code == 200
    assert client.get('/api/cart/').data['total_quantity'] == 0


def test_orders_anonymous_forbidden(client):
    response = client.get('/api/orders/')
    assert response.status_code in (401, 403)


def test_orders_authenticated(auth_client):
    response = auth_client.get('/api/orders/')
    assert response.status_code == 200


def test_order_owner_can_view(auth_client, order):
    response = auth_client.get(
        f'/api/orders/{order.id}/'
    )
    assert response.status_code == 200


def test_order_other_user_cannot_view(order):
    other_user = get_user_model().objects.create_user(
        username='otheruser',
        email='otheruser@example.com',
        password='OtherPass123!',
    )
    api_client = APIClient()
    api_client.force_authenticate(user=other_user)

    response = api_client.get(
        f'/api/orders/{order.id}/'
    )
    assert response.status_code == 404


def test_order_create_empty_cart(auth_client):
    response = auth_client.post(
        '/api/orders/',
        {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'address': 'Test Street',
        },
    )
    assert response.status_code == 400


def test_order_create_success(auth_client, book):
    auth_client.post(
        '/api/cart/add/',
        {
            'book_id': book.id,
            'quantity': 2,
            'override_quantity': False,
        },
    )

    response = auth_client.post(
        '/api/orders/',
        {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'address': 'Test Street',
        },
    )

    assert response.status_code == 201
    assert Order.objects.count() == 1
    assert OrderItem.objects.count() == 1

    book.refresh_from_db()
    assert book.stock == 8


def test_order_create_clears_cart(auth_client, book):
    auth_client.post(
        '/api/cart/add/',
        {
            'book_id': book.id,
            'quantity': 1,
            'override_quantity': False,
        },
    )

    auth_client.post(
        '/api/orders/',
        {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'address': 'Test Street',
        },
    )

    response = auth_client.get('/api/cart/')
    assert response.data['total_quantity'] == 0


def test_jwt_obtain_token(client, user):
    response = client.post(
        '/api/token/',
        {
            'username': 'testuser',
            'password': 'TestPass123!',
        },
    )

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_jwt_invalid_password(client, user):
    response = client.post(
        '/api/token/',
        {
            'username': 'testuser',
            'password': 'WrongPassword',
        },
    )

    assert response.status_code == 401


def test_jwt_refresh_token(client, user):
    token_response = client.post(
        '/api/token/',
        {
            'username': 'testuser',
            'password': 'TestPass123!',
        },
    )

    refresh_token = token_response.data['refresh']

    response = client.post(
        '/api/token/refresh/',
        {'refresh': refresh_token},
    )

    assert response.status_code == 200
    assert 'access' in response.data


def test_jwt_verify_token(client, user):
    token_response = client.post(
        '/api/token/',
        {
            'username': 'testuser',
            'password': 'TestPass123!',
        },
    )

    access_token = token_response.data['access']

    response = client.post(
        '/api/token/verify/',
        {'token': access_token},
    )

    assert response.status_code == 200


def test_jwt_invalid_token(client):
    response = client.post(
        '/api/token/verify/',
        {'token': 'invalid-token'},
    )

    assert response.status_code == 401

def test_cors_allowed_origin(client):
    response = client.get(
        '/api/books/',
        HTTP_ORIGIN='http://localhost:3000',
    )

    assert response.status_code == 200
    assert (
        response['Access-Control-Allow-Origin']
        == 'http://localhost:3000'
    )


def test_cors_disallowed_origin(client):
    response = client.get(
        '/api/books/',
        HTTP_ORIGIN='https://unknown-example.com',
    )

    assert response.status_code == 200
    assert 'Access-Control-Allow-Origin' not in response
@pytest.mark.django_db
@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '2/minute',
        },
    }
)


@pytest.mark.django_db
def test_api_throttling(monkeypatch):
    from rest_framework.throttling import AnonRateThrottle

    cache.clear()

    monkeypatch.setattr(
        AnonRateThrottle,
        'get_rate',
        lambda self: '2/minute',
    )

    api_client = APIClient()

    try:
        response1 = api_client.get('/api/books/')
        response2 = api_client.get('/api/books/')
        response3 = api_client.get('/api/books/')

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 429
    finally:
        cache.clear()
