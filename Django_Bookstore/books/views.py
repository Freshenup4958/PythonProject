from django.db import transaction
from django.core.mail import send_mail
import stripe

from django.conf import settings
from .forms import OrderCreateForm
from .models import OrderItem
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Book, Category, Order, OrderItem
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
import logging


logger = logging.getLogger('books')

class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        logger.info('Book list page was opened')
        return super().get(request, *args, **kwargs)
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')

        if category:
            queryset = queryset.filter(category_id=category)

        queryset = queryset.order_by('id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

class BookCreateView(PermissionRequiredMixin, CreateView):
    model = Book
    template_name = 'books/book_form.html'
    fields = ['category', 'title', 'author', 'price', 'description', 'stock']
    success_url = '/'
    permission_required = 'books.add_book'

class BookUpdateView(PermissionRequiredMixin, UpdateView):
    model = Book
    template_name = 'books/book_form.html'
    fields = ['category', 'title', 'author', 'price', 'description', 'stock']
    success_url = '/'
    permission_required = 'books.change_book'

class BookDeleteView(PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = '/'
    permission_required = 'books.delete_book'

def cart_detail(request):
    cart = Cart(request)

    return render(
        request,
        'books/cart_detail.html',
        {'cart': cart}
    )

def cart_add(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)

    cart.add(book=book)

    return redirect('books:cart_detail')

def cart_remove(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)

    cart.remove(book)

    return redirect('books:cart_detail')

def cart_clear(request):
        cart = Cart(request)
        cart.clear()

        return redirect('books:cart_detail')

def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
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
                    send_mail(
                        subject=f'Замовлення #{order.id} створено',
                        message=(
                            f'Дякуємо за ваше замовлення!\n\n'
                            f'Номер замовлення: #{order.id}\n'
                            f'Загальна сума: ${order.get_total_cost()}'
                        ),
                        from_email=None,
                        recipient_list=[order.email],
                    )

            cart.clear()

            return render(
                request,
                'books/order_created.html',
                {'order': order}
            )
    else:
        form = OrderCreateForm()

    return render(
        request,
        'books/order_create.html',
        {
            'cart': cart,
            'form': form,
        }
    )

def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    line_items = []

    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.book.title,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': item.quantity,
        })

    checkout_session = stripe.checkout.Session.create(
        line_items=line_items,
        mode='payment',
        success_url=(
                request.build_absolute_uri('/payment/success/')
                + '?session_id={CHECKOUT_SESSION_ID}'
        ),
        cancel_url=request.build_absolute_uri(
            '/payment/cancel/'
        ),
        metadata={
            'order_id': order.id,
        },
    )

    return redirect(checkout_session.url)
def payment_success(request):
    session_id = request.GET.get('session_id')

    if session_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY

        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status == 'paid':
            order_id = checkout_session.metadata['order_id']

            if order_id:
                Order.objects.filter(id=order_id).update(paid=True)

    return render(request, 'books/payment_success.html')


def payment_cancel(request):
    return render(request, 'books/payment_cancel.html')
async def async_book_count(request):
    count = await Book.objects.acount()

    return render(
        request,
        'books/async_book_count.html',
        {'count': count}
    )

async def async_book_detail(request, book_id):
    book = await Book.objects.select_related('category').aget(id=book_id)

    return render(
        request,
        'books/async_book_detail.html',
        {'book': book}
    )


async def async_order_count(request):
    count = await Order.objects.acount()

    return render(
        request,
        'books/async_order_count.html',
        {'count': count}
    )