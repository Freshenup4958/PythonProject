from celery import shared_task
from django.core.mail import send_mail
import csv
from pathlib import Path

from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone


@shared_task
def send_order_email(order_id):
    from .models import Order

    order = Order.objects.get(id=order_id)

    send_mail(
        subject=f"Замовлення #{order.id} створено",
        message=(
            f"Дякуємо за ваше замовлення!\n\n"
            f"Номер замовлення: #{order.id}\n"
            f"Загальна сума: ${order.get_total_cost()}"
        ),
        from_email=None,
        recipient_list=[order.email],
    )

    return f"Email sent for order #{order.id}"


@shared_task
def test_celery():
    return "Celery works!"


@shared_task
def generate_books_report():
    from .models import Book

    reports_dir = Path(settings.BASE_DIR) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_path = reports_dir / "books_report.csv"

    books = Book.objects.select_related("category").order_by("id")

    with report_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "ID",
                "Назва книги",
                "Автор",
                "Категорія",
                "Ціна",
                "Кількість на складі",
            ]
        )

        for book in books.iterator():
            writer.writerow(
                [
                    book.id,
                    book.title,
                    book.author,
                    book.category.name if book.category else "",
                    book.price,
                    book.stock,
                ]
            )

    return str(report_path)


@shared_task
def cleanup_expired_sessions():
    expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())

    deleted_count, _ = expired_sessions.delete()

    return f"Deleted {deleted_count} expired sessions"
