
from rest_framework import serializers

from .models import Stock


class StockSerializer(serializers.ModelSerializer):
    available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Stock
        fields = [
            "id",
            "book_id",
            "quantity",
            "reserved",
            "available",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]
