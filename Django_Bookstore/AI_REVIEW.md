
# AI Code Review - Django Bookstore

## 1. Функція order_create

### Original Code

```python
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
        {'cart': cart, 'form': form}
    )
```

### AI Recommendations

Під час аналізу коду за допомогою ChatGPT виявлено такі проблеми:

1. Відправлення електронного листа виконується всередині циклу створення позицій замовлення. Якщо замовлення містить декілька книг, користувач отримає декілька повідомлень.
2. Відсутня перевірка порожнього кошика. Це дозволяє створити замовлення без товарів.
3. Відправлення email виконується всередині транзакції бази даних. Якщо транзакція завершиться помилкою, повідомлення може бути відправлено для замовлення, яке не було збережене.
4. Рекомендовано використовувати `transaction.on_commit()` для відправлення повідомлення після успішного завершення транзакції.

### Final Code

```python
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
                {'order': order}
            )
    else:
        form = OrderCreateForm()

    return render(
        request,
        'books/order_create.html',
        {'cart': cart, 'form': form}
    )
```

### Result

Після внесення змін функція перевіряє наявність товарів у кошику, створює замовлення в межах атомарної транзакції та відправляє лише одне повідомлення після успішного збереження даних.


## 2. Функція payment_process

### Original Code

```python
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
        metadata={'order_id': order.id},
    )

    return redirect(checkout_session.url)
```

### AI Recommendations

Під час аналізу коду виявлено такі проблеми:

1. Відсутня перевірка статусу замовлення. Для вже оплаченого замовлення можна повторно створити платіжну сесію.
2. Не перевіряється наявність товарів у замовленні.
3. Відсутня обробка помилок Stripe API. У разі збою зовнішнього сервісу користувач отримає помилку сервера.
4. Для отримання назв книг рекомендовано використовувати `select_related('book')`, щоб зменшити кількість SQL-запитів.
5. Рекомендовано використовувати `reverse()` для формування URL-адрес замість жорстко прописаних шляхів.

### Final Code

```python
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
                'product_data': {'name': item.book.title},
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
```

### Result

Після покращення функція перевіряє стан замовлення, запобігає створенню платежу для порожнього замовлення, оптимізує SQL-запити та обробляє помилки Stripe API.


## 3. Функція payment_success

### Original Code

```python
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
```

### AI Recommendations

Під час аналізу коду за допомогою ChatGPT виявлено такі проблеми:

1. Сторінка успішної оплати відображається навіть без підтвердження платежу.
2. Відсутня перевірка наявності ідентифікатора Stripe-сесії.
3. Використання `metadata['order_id']` може спричинити помилку, якщо поле відсутнє.
4. Не обробляються помилки під час звернення до Stripe API.
5. Рекомендовано перевіряти, що платіжна сесія відповідає конкретному замовленню, а також що сума й валюта платежу збігаються з очікуваними.
6. Рекомендовано використовувати Stripe Webhooks для надійного підтвердження платежів у production-середовищі.

### Final Code

```python
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
```

### Result

Покращена функція перевіряє статус платежу, ідентифікатор замовлення, суму та валюту транзакції. У разі невдалої перевірки користувач перенаправляється на сторінку скасованої оплати.

Для production-середовища додатково рекомендовано реалізувати Stripe Webhooks та перевірку підпису подій.
