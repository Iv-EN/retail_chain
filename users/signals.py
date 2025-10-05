from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_superuser_on_migrate(sender, **kwargs):
    if sender.label == "users":
        call_command("create_superuser_command")
