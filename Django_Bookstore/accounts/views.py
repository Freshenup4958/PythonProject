from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    """
    Реєструє нового користувача в системі.

    Обробляє GET-запит для відображення форми реєстрації.
    Під час POST-запиту перевіряє введені дані, створює
    користувача та автоматично авторизує його.

    Після успішної реєстрації перенаправляє користувача
    до каталогу книг.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('books:book_list')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})