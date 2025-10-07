from django import forms
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import NetworkObject, Product
from decimal import Decimal # Импортируем Decimal


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean_network_object(self):
        network_object = self.cleaned_data.get('network_object')
        if network_object:
            pass
        return network_object