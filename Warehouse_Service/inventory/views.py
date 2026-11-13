
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions

from .models import Stock
from .serializers import StockSerializer


class StockPermissions(DjangoModelPermissions):
    perms_map = {
        "GET": ["inventory.view_stock"],
        "HEAD": ["inventory.view_stock"],
        "OPTIONS": ["inventory.view_stock"],
        "POST": ["inventory.add_stock"],
        "PUT": ["inventory.change_stock"],
        "PATCH": ["inventory.change_stock"],
        "DELETE": ["inventory.delete_stock"],
    }


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all().order_by("book_id")
    serializer_class = StockSerializer
    permission_classes = [StockPermissions]
    lookup_field = "book_id"
