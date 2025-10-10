from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from network.models import NetworkObject


@receiver(pre_save, sender=NetworkObject)
def check_network_constraints(sender, instance, **kwargs):
    """
    Проверяет ограничения на глубину и циклические связи для NetworkObject.
    """
    if instance.supplier is not None and instance.pk == instance.supplier.pk:
        raise ValidationError("Объект не может быть своим поставщиком.")
    distance = 0
    node = instance.supplier
    visiting = set()
    while node is not None:
        if node.pk in visiting:
            raise ValidationError(
                "Обнаружена циклическая зависимость в цепочке поставщиков."
            )
        visiting.add(node.pk)
        distance += 1
        if distance > 2:
            raise ValidationError(
                "Глубина сети не может превышать 3 уровня (включая завод)."
            )
        node = node.supplier
