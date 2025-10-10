import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from network.models import NetworkObject
from users.models import User

from .base_test_case import BaseTestCase

NETWORK_OBJECTS_URL = reverse("network:network_objects-list")


class NetworkObjectTests(BaseTestCase):
    """Тесты для модели NetworkObject и NetworkObjectViewSet."""

    def test_create_network_object_success(self):
        """Тестирование успешного создания объекта NetworkObject."""
        data = {
            "name": "Новый объект",
            "email": "new_obj@example.com",
            "country": "Украина",
            "city": "Киев",
            "street": "Крещатик",
            "house_number": "1",
            "debt_to_supplier": "500.50",
        }
        response = self.client.post(NETWORK_OBJECTS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkObject.objects.count(), 1)
        self.assertEqual(NetworkObject.objects.get().name, data["name"])

    def test_create_network_object_missing_required_field(self):
        """Тестирование создания объекта с пропущенным обязательным полем."""
        data = {
            "email": "e@e.ru",
            "country": "Россия",
            "city": "Москва",
            "street": "Пушкинская",
            "house_number": "20",
        }
        response = self.client.post(NETWORK_OBJECTS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_network_object_invalid_email(self):
        """Тестирование создания объекта с некорректным email."""
        data = {
            "name": "Объект с плохим email",
            "email": "invalid-email",
            "country": "Россия",
            "city": "Москва",
            "street": "Пушкинская",
            "house_number": "20",
        }
        response = self.client.post(NETWORK_OBJECTS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_list_network_objects(self):
        """Тестирование получения списка объектов NetworkObject."""
        self.create_network_object(name="Объект 1")
        self.create_network_object(name="Объект 2")
        response = self.client.get(NETWORK_OBJECTS_URL, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_network_object(self):
        """Тестирование получения одного объекта NetworkObject."""
        network_object = self.create_network_object(name="Детальный объект")
        url = reverse(
            "network:network_objects-detail", kwargs={"pk": network_object.pk}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Детальный объект")

    def test_update_network_object_success(self):
        """Тестирование успешного обновления объекта NetworkObject."""
        network_object = self.create_network_object(name="Старый объект")
        url = reverse(
            "network:network_objects-detail", kwargs={"pk": network_object.pk}
        )
        new_data = {
            "name": "Обновленный объект",
            "email": "updated@example.com",
            "country": "Беларусь",
            "city": "Минск",
            "street": "Независимости",
            "house_number": "10",
            "debt_to_supplier": "200.00",
        }
        response = self.client.put(url, new_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        network_object.refresh_from_db()
        self.assertEqual(network_object.name, "Обновленный объект")
        self.assertEqual(network_object.country, "Беларусь")

    def test_update_network_object_invalid_data(self):
        """Тестирование обновления объекта с недопустимыми данными."""
        network_object = self.create_network_object()
        url = reverse(
            "network:network_objects-detail", kwargs={"pk": network_object.pk}
        )
        invalid_data = {
            "name": "Обновленный объект",
            "email": "invalid-email",  # Некорректный email
            "country": "Россия",
            "city": "Москва",
            "street": "Пушкинская",
            "house_number": "20",
        }
        response = self.client.put(url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_delete_network_object_success(self):
        """Тестирование успешного удаления объекта NetworkObject."""
        network_object = self.create_network_object()
        url = reverse(
            "network:network_objects-detail", kwargs={"pk": network_object.pk}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(NetworkObject.objects.count(), 0)

    def test_filter_by_country(self):
        """Тестирование фильтрации объектов по стране."""
        self.create_network_object(name="Российский объект", country="Россия")
        self.create_network_object(name="Украинский объект", country="Украина")
        self.create_network_object(name="Еще один российский", country="Россия")

        url = f"{NETWORK_OBJECTS_URL}?country=Россия"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for obj in response.data:
            self.assertEqual(obj["country"], "Россия")

    def test_level_property_factory(self):
        """Тестирование определения уровня для завода (уровень 0)."""
        obj = self.create_network_object(supplier=None)
        self.assertEqual(obj.level, 0)

    def test_level_property_retail_network(self):
        """Тестирование определения уровня для розничной сети (уровень 1)."""
        supplier = self.create_network_object(supplier=None)
        obj = self.create_network_object(supplier=supplier)
        self.assertEqual(obj.level, 1)

    def test_level_property_individual_entrepreneur(self):
        """
        Тестирование определения уровня для индивидуального
        предпринимателя (уровень 2).
        """
        supplier_level1 = self.create_network_object(supplier=None)
        supplier_level2 = self.create_network_object(supplier=supplier_level1)
        obj = self.create_network_object(supplier=supplier_level2)
        self.assertEqual(obj.level, 2)

    def test_level_property_exceeding_three_links(self):
        """Тестирование валидации превышения 3 звеньев."""
        supplier_level1 = self.create_network_object(supplier=None)
        supplier_level2 = self.create_network_object(supplier=supplier_level1)
        supplier_level3 = self.create_network_object(supplier=supplier_level2)
        with pytest.raises(ValidationError) as excinfo:
            self.create_network_object(
                supplier=supplier_level3, name="Exceeding Object"
            )
        self.assertIn(
            "Цепочка поставщиков не может содержать более 3 звеньев.",
            str(excinfo.value),
        )

    def test_str_representation(self):
        """Тестирование строкового представления объекта."""
        obj = self.create_network_object(name="Тестовый Объект", supplier=None)
        self.assertEqual(str(obj), "Тестовый Объект(Завод)")

    def test_clean_self_supplier_validation(self):
        """
        Тестирование валидации, запрещающей быть своим собственным поставщиком.
        """
        obj = self.create_network_object()
        obj.supplier = obj
        with pytest.raises(ValidationError) as excinfo:
            obj.full_clean()
        self.assertIn(
            "Объект не может быть своим собственным поставщиком.",
            excinfo.value.messages,
        )

    def test_clean_circular_dependency_validation(self):
        """Тестирование валидации циклической зависимости."""
        supplier1 = self.create_network_object(name="Supplier 1")
        supplier2 = self.create_network_object(name="Supplier 2", supplier=supplier1)
        supplier1.supplier = supplier2  # Создаем цикл
        with pytest.raises(ValidationError) as excinfo:
            supplier1.full_clean()
        self.assertIn("Обнаружена циклическая связь.", excinfo.value.messages)
