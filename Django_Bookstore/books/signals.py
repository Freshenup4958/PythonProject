from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Book, Category


def invalidate_book_cache():
    cache.clear()


@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def clear_book_cache(sender, instance, **kwargs):
    transaction.on_commit(invalidate_book_cache)
