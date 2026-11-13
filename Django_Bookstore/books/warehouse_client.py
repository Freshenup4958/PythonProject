
import logging
import os

import requests

logger = logging.getLogger(__name__)

WAREHOUSE_API_URL = os.getenv(
    "WAREHOUSE_API_URL",
    "http://127.0.0.1:8001/api",
)


def get_book_stock(book_id):
    """Получить остатки книги из Warehouse Service."""
    username = os.getenv("WAREHOUSE_USERNAME")
    password = os.getenv("WAREHOUSE_PASSWORD")

    if not username or not password:
        logger.error("Warehouse credentials are not configured")
        return None

    try:
        token_response = requests.post(
            f"{WAREHOUSE_API_URL}/token/",
            json={"username": username, "password": password},
            timeout=5,
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access"]

        stock_response = requests.get(
            f"{WAREHOUSE_API_URL}/stocks/{book_id}/",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5,
        )
        stock_response.raise_for_status()

        return stock_response.json()

    except (requests.RequestException, KeyError, ValueError):
        logger.exception(
            "Failed to fetch stock for book_id=%s",
            book_id,
        )
        return None
