from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean_network_object(self):
        network_object = self.cleaned_data.get("network_object")
        if network_object:
            pass
        return network_object
