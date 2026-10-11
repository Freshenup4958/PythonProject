from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'address',
        ]

        labels = {
            'first_name': _('First name'),
            'last_name': _('Last name'),
            'email': _('Email'),
            'address': _('Address'),
        }