
import logging

from celery import shared_task

from .models import Stock
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


@shared_task
def check_low_stock(threshold=5):
    """Проверяет книги с низким складским остатком."""
    low_stock = []

    for stock in Stock.objects.all():
        if stock.available < threshold:
            low_stock.append({
                "book_id": stock.book_id,
                "available": stock.available,
            })

    logger.info(
        _("Low stock check completed: %s books found"),
        len(low_stock),
    )

    return low_stock
