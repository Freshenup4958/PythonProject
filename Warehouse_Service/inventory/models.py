
from django.db import models


class Stock(models.Model):
    book_id = models.PositiveIntegerField(unique=True)
    quantity = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available(self):
        return self.quantity - self.reserved

    def __str__(self):
        return f"Book {self.book_id}: {self.available} available"
