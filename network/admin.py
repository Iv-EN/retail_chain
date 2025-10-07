from decimal import Decimal

from django.db import transaction
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.forms import ValidationError

from .models import NetworkObject, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "release_date", "network_object")
    list_filter = ("network_object__name",)
    search_fields = ("name", "model", "release_date", "network_object")


class ProductInLine(admin.TabularInline):
    model = Product
    extra = 0
    can_delete = True


@admin.register(NetworkObject)
class NetworkObjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "country",
        "city",
        "supplier_link",
        "debt_to_supplier",
        "level",
        "created_at",
    )
    list_filter = ("city",)
    readonly_fields = ("created_at",)
    inlines = [ProductInLine]

    def supplier_link(self, obj):
        """Метод для отображения ссылки на поставщика."""
        if obj.supplier:
            link = reverse(
                "admin:network_networkobject_change", args=[obj.supplier.id]
            )
            return format_html('<a href="{}">{}</a>', link, obj.supplier.name)
        return "Поставщик отсутствует"

    supplier_link.short_description = "Поставщик"

    def level(self, obj):
        """Метод для отображения уровня иерархии."""
        try:
            return obj.level
        except ValidationError as error:
            return format_html('<span style="color: red;">{}</span>', error)

    level.short_description = "Уровень"

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
                request, "Объектов с задолженностью нет.", messages.WARNING
            )

    clear_debt.short_description = "Очистить задолженность перед поставщиком"
    
    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
        except ValidationError as error:
            form._errors = error.message_dict
            return 
        super().save_model(request, obj, form, change)