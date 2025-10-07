from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import NetworkObject


@receiver(pre_save, sender=NetworkObject)
def check_cyclic_dependency(sender, instance, **kwargs):
    """
    Проверяет наличие циклической связи перед сохранением объекта.
    """
    if instance.supplier and instance.supplier.pk == instance.pk:
        raise ValidationError({'supplier': "Объект не может быть поставщиком у самого себя"})
    visiting = set()
    node = instance.supplier
    distance = 0
    while node is not None:
        if node.pk == instance.pk:
            raise ValidationError(
                "Обнаружена попытка создать циклическую связь (поставщик ссылается на сам объект)"
            )
        if node.pk in visiting:
            raise ValidationError(
                "В цепочке поставщиков обнаружена циклическая связь"
            )
        visiting.add(node.pk)
        distance += 1
        if distance > 2: # Проверяем глубину сети
            raise ValidationError(
                "Глубина сети не может превышать 3 уровня"
            )
        node = node.supplier
