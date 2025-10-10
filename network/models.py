from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction


class NetworkObject(models.Model):
    """Описывает звено сети."""

    name = models.CharField(max_length=255, verbose_name="Наименование")
    email = models.EmailField(blank=True, verbose_name="Электронная почта")
    country = models.CharField(max_length=100, verbose_name="Страна")
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=255, verbose_name="Улица")
    house_number = models.CharField(max_length=5, verbose_name="Номер дома")
    supplier = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subordinates",
        verbose_name="Поставщик",
    )
    debt_to_supplier = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Долг перед поставщиком",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время создания"
    )

    class Meta:
        verbose_name = "Звено сети"
        verbose_name_plural = "Звенья сети"

    def __str__(self):
        return f"{self.name}({self.get_level_display()})"

    @property
    def level(self):
        """
        Вычисляет уровень иерархии объекта.
        """
        distance = 0
        node = self.supplier
        visiting = set()
        while node is not None:
            visiting.add(node.pk)
            distance += 1
            if distance > 2:
                return -2
            node = node.supplier
        return distance

    def get_level_display(self):
        """Отображает уровень иерархии в виде строки."""
        lvl = self.level
        if lvl is None:
            return "Обнаружена проблема в цепочке поставщиков"
        if lvl == -1:
            return "Обнаружена циклическая связь"
        if lvl == -2:
            return "цепочка поставщиков превышает 3 звена"
        if lvl == 0:
            return "Завод"
        elif lvl == 1:
            return "Розничная сеть"
        else:
            return "Индивидуальный предприниматель"

    def clean(self):
        """
        Выполняет дополнительные проверки перед сохранением объекта.
        """
        if self.debt_to_supplier < Decimal("0.00"):
            raise ValidationError(
                {"debt_to_supplier": "Долг не может быть отрицательным."}
            )
        if self.supplier and self.supplier.pk == self.pk:
            raise ValidationError(
                "Объект не может быть своим собственным поставщиком."
            )
        if self.supplier:
            current_node = self.supplier
            distance = 0
            while current_node is not None:
                if current_node.pk == self.pk:
                    raise ValidationError("Обнаружена циклическая связь.")
                distance += 1
                if distance > 2:
                    raise ValidationError(
                        """
                        Цепочка поставщиков не может содержать более 3 звеньев.
                        """
                    )
                current_node = current_node.supplier

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.full_clean()
            super().save(*args, **kwargs)


class Product(models.Model):
    """Описывает продукт."""

    name = models.CharField(max_length=255, verbose_name="Название продукта")
    model = models.CharField(max_length=255, verbose_name="Модель продукта")
    release_date = models.DateField(verbose_name="Дата выхода на рынок")
    network_object = models.ForeignKey(
        NetworkObject,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Звено сети",
    )

    class Meta:
        verbose_name: "Продукт"  # noqa: F821
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.name} ({self.model})"
