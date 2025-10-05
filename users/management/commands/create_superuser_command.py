import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """
    Создает суперпользователя,
    если его не существует и установлены переменные .env.
    """

    def handle(self, *args, **options):
        email_host_user = os.getenv("ADMIN_EMAIL")
        user_set_username = os.getenv("ADMIN_USERNAME")
        user_set_password = os.getenv("ADMIN_PASSWORD")
        if not all([email_host_user, user_set_password, user_set_username]):
            self.stdout.write(
                self.style.WARNING(
                    """Не все необходимые переменные окружения установлены для
                создания суперпользователя.
                Пропускается."""
                )
            )
            return
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.SUCCESS(
                    "Суперпользователь уже существует. Создание пропускается."
                )
            )
            return
        try:
            user = User.objects.create(
                email=email_host_user,
                username=user_set_username,
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )
            user.set_password(user_set_password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Суперпользователь создан: {user.username} <{user.email}>"
                )
            )
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(f"Ошибка создания суперпользователя: {error}")
            )
