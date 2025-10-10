from decimal import Decimal

from django import forms
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from .models import NetworkObject, Product


# class ProductSelectorForm(forms.ModelForm):
#     product_selector = forms.ModelChoiceField(
#         queryset=Product.objects.none(),
#         required=False,
#         label="Выбрать существующий продукт",
#         help_text="Выберите продукт, связанный с поставщиком.",
#     )
#
#     class Meta:
#         model = Product
#         fields = ["product_selector"]
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         request = self.request if hasattr(self, "request") else kwargs.get("request")
#         network_object = None
#         if (
#             request
#             and request.resolver_match
#             and "object_id" in request.resolver_match.kwargs
#         ):
#             try:
#                 network_object_id = request.resolver_match.kwargs["object_id"]
#                 network_object = NetworkObject.objects.get(pk=network_object_id)
#             except (AttributeError, KeyError, NetworkObject.DoesNotExist):
#                 pass
#         if (
#             not network_object
#             and isinstance(self.instance, Product)
#             and self.instance.network_object
#         ):
#             network_object = self.instance.network_object
#         if network_object and network_object.supplier:
#             self.fields["product_selector"].queryset = Product.objects.filter(
#                 network_object=network_object.supplier
#             )
#         else:
#             self.fields["product_selector"].queryset = Product.objects.none()
#
#     def clean(self):
#         cleaned_data = super().clean()
#         product_selector = cleaned_data.get("product_selector")
#         if not product_selector and self.instance.pk is None:
#             raise forms.ValidationError("Необходимо выбрать существующий продукт.")
#         if product_selector:
#             cleaned_data["name"] = product_selector.name
#             cleaned_data["model"] = product_selector.model
#             cleaned_data["release_date"] = product_selector.release_date
#         return cleaned_data


class ProductInlineFormSet(admin.TabularInline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        obj = kwargs.get("instance")
        if obj and obj.level != 0:
            self.can_add = False

    def get_form(self, **kwargs):
        try:
            network_object_id = self.request.resolver_match.kwargs["object_id"]
            network_object = NetworkObject.objects.get(pk=network_object_id)
        except (AttributeError, KeyError, NetworkObject.DoesNotExist):
            network_object = None

        if network_object and network_object.level != 0:
            kwargs["form"] = ProductSelectorForm
        else:
            kwargs["form"] = ProductInlineForm
        return super().get_form(**kwargs)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "release_date", "network_object")
    list_filter = ("network_object__name",)
    search_fields = ("name", "model", "release_date", "network_object")


class ProductInlineForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "model", "release_date", "network_object"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk is None:
            if "network_object" in self.initial:
                network_obj_instance = self.initial["network_object"]
                if (
                    not isinstance(network_obj_instance, NetworkObject)
                    or network_obj_instance.level != 0
                ):
                    raise forms.ValidationError(
                        "Продукты можно создавать только для заводов."
                    )
                self.fields["network_object"].disabled = True
        elif self.instance and self.instance.pk:
            pass
        elif self.instance and self.instance.pk:
            pass

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    can_delete = True
    fk_name = "network_object"

    def has_add_permission(self, request, obj):
        if obj and hasattr(obj, "level") and obj.level == 0:
            return True
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs


@admin.register(NetworkObject)
class NetworkObjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "country",
        "city",
        "supplier_link",
        "debt_to_supplier",
        "level_display",
        "created_at",
    )
    list_filter = ("city",)
    readonly_fields = ("created_at",)
    inlines = [ProductInline]

    def supplier_link(self, obj):
        """Метод для отображения ссылки на поставщика."""
        if obj.supplier:
            link = reverse(
                "admin:network_networkobject_change",
                args=[obj.supplier.id]
            )
            return format_html(
                '<a href="{}">{}</a>',
                link, obj.supplier.name
            )
        return "Поставщик отсутствует"

    supplier_link.short_description = "Поставщик"

    def level_display(self, obj):
        """Метод для отображения уровня иерархии."""
        return obj.get_level_display()

    level_display.short_description = "Уровень"
    level_display.admin_order_field = "Level"

    actions = ["clear_debt"]
    """Admin action для очистки задолженности."""

    def clear_debt(self, request, queryset):
        """Метод для очистки задолженности перед поставщиком."""
        update_count = 0
        for obj in queryset:
            if obj.debt_to_supplier > Decimal("0.00"):
                obj.debt_to_supplier = Decimal("0.00")
                obj.save()
                update_count += 1
        if update_count > 0:
            self.message_user(
                request,
                f"Для {update_count} "
                f"объектов задолженность перед поставщиком успешно очищена.",
            )
        else:
            self.message_user(
                request,
                "Объектов с задолженностью нет.",
                messages.WARNING
            )

    clear_debt.short_description = "Очистить задолженность перед поставщиком"
