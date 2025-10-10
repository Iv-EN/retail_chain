from django.urls import reverse

from users.models import User

from .base_test_case import BaseTestCase


class TestUser(BaseTestCase):

    def test_create_user(self):
        """Проверка создания нового пользователя."""
        data = {
            "username": "new_test_user",
            "email": "test@email.ru",
            "password": "test",
            "phone": "123456789",
        }
        response = self.client.post("/users/", data=data)
        assert response.status_code == 201
        assert User.objects.last().username == "new_test_user"
        assert User.objects.count() == 2

    def test_create_user_with_existing_email(self):
        """Проверка создания пользователя с уже существующим email."""
        data = {
            "username": "new_test_user",
            "email": "test_email",
            "password": "123",
            "phone": "123456789",
        }
        response = self.client.post("/users/", data=data)
        assert response.status_code == 400
        assert "email" in response.data
