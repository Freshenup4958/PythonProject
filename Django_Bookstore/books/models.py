from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Category(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Book(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name=_('Category')
    )
    title = models.CharField(_('Title'), max_length=200)
    author = models.CharField(_('Author'), max_length=150)
    price = models.DecimalField(_('Price'), max_digits=8, decimal_places=2)
    description = models.TextField(_('Description'), blank=True)
    stock = models.PositiveIntegerField(_('Stock'), default=0)

    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')

    def __str__(self):
        return self.title


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    first_name = models.CharField(_('First name'), max_length=100)
    last_name = models.CharField(_('Last name'), max_length=100)
    email = models.EmailField(_('Email'))
    address = models.CharField(_('Address'), max_length=250)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    paid = models.BooleanField(_('Paid'), default=False)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_('Order')
    )
    book = models.ForeignKey(
        Book,
        related_name='order_items',
        on_delete=models.CASCADE,
        verbose_name=_('Book')
    )
    price = models.DecimalField(_('Price'), max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)

    class Meta:
        verbose_name = _('Order item')
        verbose_name_plural = _('Order items')

    def __str__(self):
        return f'{self.book.title} x {self.quantity}'

    def get_cost(self):
        return self.price * self.quantity