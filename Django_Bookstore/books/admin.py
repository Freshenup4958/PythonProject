from django.contrib import admin
from .models import Book, Category, Order, OrderItem


class BookInline(admin.TabularInline):
    model = Book
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BookInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price', 'stock')
    list_filter = ('category', 'author')
    search_fields = ('title', 'author')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'created',
        'paid',
    )
    list_filter = ('paid', 'created')
    search_fields = ('first_name', 'last_name', 'email')
    inlines = [OrderItemInline]

