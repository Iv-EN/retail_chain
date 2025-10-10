from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from network.models import NetworkObject
from users.models import User


class BaseTestCase(APITestCase):
    """Базовый тестовый класс."""

    def setUp(self):
        """Метод для инициализации тестов."""
        self.user = self.create_user()
        self.client.force_authenticate(user=self.user)

    def create_user(self, **kwargs):
        """Создание пользователя с заданными параметрами."""
        default_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test",
            "phone": "123456789",
        }
        default_data.update(kwargs)
        return User.objects.create(**default_data)

    def create_network_object(self, **kwargs):
        """Создание звена цепи с заданными параметрами."""
        default_data = {
            "name": "Объект",
            "email": "e@e.ru",
            "country": "Россия",
            "city": "Москва",
            "street": "Пушкинская",
            "house_number": "20",
            "debt_to_supplier": "1000.00",
        }
        default_data.update(kwargs)
        return NetworkObject.objects.create(**default_data)
