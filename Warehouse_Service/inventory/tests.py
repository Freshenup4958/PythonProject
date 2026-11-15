
import pytest

from inventory.models import Stock


@pytest.mark.django_db
def test_stock_creation():
    stock = Stock.objects.create(
        book_id=1,
        quantity=10,
        reserved=3,
    )

    assert stock.book_id == 1
    assert stock.quantity == 10
    assert stock.reserved == 3
    assert stock.available == 7


@pytest.mark.django_db
def test_stock_without_reservations():
    stock = Stock.objects.create(
        book_id=2,
        quantity=5,
    )

    assert stock.reserved == 0
    assert stock.available == 5


@pytest.mark.django_db
def test_stock_string_representation():
    stock = Stock.objects.create(
        book_id=3,
        quantity=8,
        reserved=2,
    )

    assert str(stock) == "Book 3: 6 available"


@pytest.mark.django_db
def test_stock_unique_book_id():
    from django.db import IntegrityError

    Stock.objects.create(book_id=4, quantity=10)

    with pytest.raises(IntegrityError):
        Stock.objects.create(book_id=4, quantity=5)

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_stock_api_requires_authentication():
    Stock.objects.create(book_id=1, quantity=10)

    client = APIClient()
    response = client.get("/api/stocks/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_stock_api_with_permission():
    user = get_user_model().objects.create_user(
        username="reader",
        password="test-password-123",
    )
    permission = Permission.objects.get(codename="view_stock")
    user.user_permissions.add(permission)

    Stock.objects.create(book_id=1, quantity=10, reserved=2)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/stocks/1/")

    assert response.status_code == 200
    assert response.data["available"] == 8


@pytest.mark.django_db
def test_stock_api_without_permission():
    user = get_user_model().objects.create_user(
        username="no_permission",
        password="test-password-123",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/stocks/")

    assert response.status_code == 403

@pytest.mark.django_db
def test_jwt_authentication():
    user = get_user_model().objects.create_user(
        username="jwt_reader",
        password="test-password-123",
    )

    permission = Permission.objects.get(
        codename="view_stock",
        content_type__app_label="inventory",
    )
    user.user_permissions.add(permission)

    Stock.objects.create(book_id=5, quantity=12, reserved=2)

    client = APIClient()

    response = client.post(
        "/api/token/",
        {
            "username": "jwt_reader",
            "password": "test-password-123",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data

    access_token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = client.get("/api/stocks/5/")

    assert response.status_code == 200
    assert response.data["available"] == 10

from inventory.tasks import check_low_stock


@pytest.mark.django_db
def test_check_low_stock():
    Stock.objects.create(book_id=10, quantity=10, reserved=0)
    Stock.objects.create(book_id=11, quantity=4, reserved=1)
    Stock.objects.create(book_id=12, quantity=2, reserved=0)

    result = check_low_stock(threshold=5)

    assert result == [
        {"book_id": 11, "available": 3},
        {"book_id": 12, "available": 2},
    ]
