
import logging

import stripe
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .cart import Cart
from .forms import OrderCreateForm
from .models import Book, Category, Order, OrderItem


logger = logging.getLogger('books')


class BookListView(ListView):
    """Відображає каталог книг із фільтрацією та пагінацією."""

    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        """Обробляє запит на перегляд каталогу книг."""
        logger.info('Book list page was opened')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Повертає книги з урахуванням вибраної категорії."""
        queryset = super().get_queryset()
        category = self.request.GET.get('category')

        if category:
            queryset = queryset.filter(category_id=category)

        queryset = queryset.order_by('id')
        return queryset

    def get_context_data(self, **kwargs):
        """Додає категорії та вибраний фільтр до контексту."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        return context


class BookDetailView(DetailView):
    """Відображає детальну інформацію про вибрану книгу."""

    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'


class BookCreateView(PermissionRequiredMixin, CreateView):
    """Дозволяє користувачам із відповідними правами додавати книги."""

    model = Book
    template_name = 'books/book_form.html'
    fields = [
        'category', 'title', 'author',
        'price', 'description', 'stock',
    ]
    success_url = '/'
    permission_required = 'books.add_book'


class BookUpdateView(PermissionRequiredMixin, UpdateView):
    """Дозволяє користувачам із відповідними правами редагувати книги."""

    model = Book
    template_name = 'books/book_form.html'
    fields = [
        'category', 'title', 'author',
        'price', 'description', 'stock',
    ]
    success_url = '/'
    permission_required = 'books.change_book'


class BookDeleteView(PermissionRequiredMixin, DeleteView):
    """Дозволяє користувачам із відповідними правами видаляти книги."""

    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = '/'
    permission_required = 'books.delete_book'


def cart_detail(request):
    """Відображає поточний вміст кошика покупок."""
    cart = Cart(request)

    return render(
        request,
        'books/cart_detail.html',
        {'cart': cart},
    )


def cart_add(request, book_id):
    """Додає вибрану книгу до кошика покупок."""
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)

    cart.add(book=book)

    return redirect('books:cart_detail')


def cart_remove(request, book_id):
    """Видаляє вибрану книгу з кошика покупок."""
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)

    cart.remove(book)

    return redirect('books:cart_detail')


def cart_clear(request):
    """Очищує кошик покупок."""
    cart = Cart(request)
    cart.clear()

    return redirect('books:cart_detail')


# Generated with AI, reviewed and modified
def order_create(request):
    """Створює замовлення з кошика та надсилає підтвердження."""
    cart = Cart(request)

    if request.method == 'POST':
        if len(cart) == 0:
            return redirect('books:cart_detail')

        form = OrderCreateForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                order = form.save()

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        book=item['book'],
                        price=item['price'],
                        quantity=item['quantity'],
                    )

                total_cost = order.get_total_cost()

                transaction.on_commit(
                    lambda: send_mail(
                        subject=f'Замовлення #{order.id} створено',
                        message=(
                            f'Дякуємо за ваше замовлення!\n\n'
                            f'Номер замовлення: #{order.id}\n'
                            f'Загальна сума: ${total_cost}'
                        ),
                        from_email=None,
                        recipient_list=[order.email],
                    )
                )

            cart.clear()

            return render(
                request,
                'books/order_created.html',
                {'order': order},
            )
    else:
        form = OrderCreateForm()

    return render(
        request,
        'books/order_create.html',
        {'cart': cart, 'form': form},
    )


# Generated with AI, reviewed and modified
def payment_process(request, order_id):
    """Створює Stripe Checkout Session для неоплаченого замовлення."""
    order = get_object_or_404(Order, id=order_id)

    if order.paid:
        return redirect('books:payment_success')

    items = list(order.items.select_related('book'))

    if not items:
        return redirect('books:cart_detail')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    line_items = [
        {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.book.title,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': item.quantity,
        }
        for item in items
    ]

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=(
                request.build_absolute_uri(
                    reverse('books:payment_success')
                )
                + '?session_id={CHECKOUT_SESSION_ID}'
            ),
            cancel_url=request.build_absolute_uri(
                reverse('books:payment_cancel')
            ),
            metadata={'order_id': str(order.id)},
        )
    except stripe.StripeError:
        logger.exception('Stripe Checkout Session creation failed')
        return redirect('books:cart_detail')

    return redirect(checkout_session.url)


# Generated with AI, reviewed and modified
def payment_success(request):
    """Перевіряє Stripe-сесію та підтверджує оплату замовлення."""
    session_id = request.GET.get('session_id')

    if not session_id:
        return redirect('books:payment_cancel')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        logger.exception('Stripe payment verification failed')
        return redirect('books:payment_cancel')

    if checkout_session.payment_status != 'paid':
        return redirect('books:payment_cancel')

    metadata = checkout_session.metadata or {}
    order_id = metadata.get('order_id')

    if not order_id:
        return redirect('books:payment_cancel')

    order = Order.objects.filter(id=order_id).first()

    if order is None:
        return redirect('books:payment_cancel')

    expected_amount = int(order.get_total_cost() * 100)

    if (
        checkout_session.amount_total != expected_amount
        or checkout_session.currency != 'usd'
    ):
        logger.warning('Stripe payment amount or currency mismatch')
        return redirect('books:payment_cancel')

    if not order.paid:
        order.paid = True
        order.save(update_fields=['paid'])

    return render(request, 'books/payment_success.html')


def payment_cancel(request):
    """Відображає сторінку скасованої оплати."""
    return render(request, 'books/payment_cancel.html')


async def async_book_count(request):
    """Асинхронно отримує та відображає кількість книг."""
    count = await Book.objects.acount()

    return render(
        request,
        'books/async_book_count.html',
        {'count': count},
    )


async def async_book_detail(request, book_id):
    """Асинхронно отримує детальну інформацію про книгу."""
    book = await Book.objects.select_related('category').aget(id=book_id)

    return render(
        request,
        'books/async_book_detail.html',
        {'book': book},
    )


async def async_order_count(request):
    """Асинхронно отримує та відображає кількість замовлень."""
    count = await Order.objects.acount()

    return render(
        request,
        'books/async_order_count.html',
        {'count': count},
    )
