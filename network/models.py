from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

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
            if node.pk in visiting:
                raise ValidationError(
                    "В цепочке поставщиков обнаружена циклическая связь"
                )
            visiting.add(node.pk)
            distance += 1
            if distance > 2:
                raise ValidationError("Глубина сети не может превышать 2 уровней")
            node = node.supplier
        return distance

    def get_level_display(self):
        """Отображает уровень иерархии в виде строки."""
        try:
            lvl = self.level
            if lvl == 0:
                return "Завод"
            elif lvl == 1:
                return "Розничная сеть"
            else:
                return f"Уровень {lvl} (индивидуальный предприниматель)"
        except ValidationError as error:
            return f"Ошибка уровня: {error}"

    def _validate_no_cycles(self):
        """Защита на уровне валидации."""
        visiting = set()
        node = self.supplier
        distance = 0
        while node is not None:
            if node.pk in visiting:
                raise ValidationError(
                    "В цепочке поставщиков обнаружена циклическая связь"
                )
            visiting.add(node.pk)
            distance += 1
            if distance > 2:
                raise ValidationError("Глубина сети не может превышать 2 уровней")
            node = node.supplier

    def clean(self):
        """Валидация перед сохранением в базу."""
        self._validate_no_cycles()


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
        verbose_name: "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.name} ({self.model})"
