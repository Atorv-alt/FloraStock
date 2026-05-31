"""Модульные тесты для ApiService"""

import json
from unittest.mock import patch, MagicMock
import pytest
import requests
from src.services.api_service import ApiService


@pytest.fixture
def api():
    return ApiService("http://localhost:5000/api")


class MockResponse:
    def __init__(self, data, status_code=200, headers=None):
        self._data = data
        self.status_code = status_code
        self.headers = headers or {"Content-Type": "application/json"}

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(
                f"HTTP {self.status_code}",
                response=self
            )

    @property
    def content(self):
        return json.dumps(self._data).encode() if self._data else b""


class TestApiService:
    def test_login_success(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse({
            "token": "test_token",
            "employee": {"id": 1, "fullName": "Admin"}
        })):
            result = api.login("admin", "admin")
            assert result["token"] == "test_token"
            assert api.token == "test_token"

    def test_set_token(self, api):
        api.set_token("my_token")
        assert api.token == "my_token"
        assert api.session.headers["Authorization"] == "Bearer my_token"

    def test_clear_token(self, api):
        api.set_token("my_token")
        api.clear_token()
        assert api.token is None
        assert "Authorization" not in api.session.headers

    def test_get_products(self, api):
        expected = [{"id": 1, "name": "Роза"}, {"id": 2, "name": "Тюльпан"}]
        with patch.object(api.session, 'request', return_value=MockResponse(expected)):
            result = api.get_products()
            assert result == expected

    def test_get_products_empty(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse([])):
            result = api.get_products()
            assert result == []

    def test_get_categories(self, api):
        expected = [{"id": 1, "name": "Розы"}]
        with patch.object(api.session, 'request', return_value=MockResponse(expected)):
            result = api.get_categories()
            assert result == expected

    def test_create_product(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse({"id": 1, "name": "Роза"})):
            result = api.create_product(name="Роза", retailPrice=150.0)
            assert result["id"] == 1
            assert result["name"] == "Роза"

    def test_delete_product_success(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse({})):
            result = api.delete_product(1)
            assert result is True

    def test_delete_product_failure(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse({}, status_code=404)):
            result = api.delete_product(999)
            assert result is False

    def test_get_clients(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse([
            {"id": 1, "fullName": "Иван"}
        ])):
            result = api.get_clients()
            assert len(result) == 1
            assert result[0]["fullName"] == "Иван"

    def test_get_orders(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse([
            {"id": 1, "orderNumber": "ORD-001"}
        ])):
            result = api.get_orders()
            assert result[0]["orderNumber"] == "ORD-001"

    def test_get_inventory(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse([
            {"id": 1, "quantity": 10}
        ])):
            result = api.get_inventory()
            assert result[0]["quantity"] == 10

    def test_get_suppliers(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse([
            {"id": 1, "name": "ООО Цветы"}
        ])):
            result = api.get_suppliers()
            assert result[0]["name"] == "ООО Цветы"

    def test_get_batches(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse([
            {"id": 1, "invoiceNumber": "INV-001"}
        ])):
            result = api.get_batches()
            assert result[0]["invoiceNumber"] == "INV-001"

    def test_get_inventory_value(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse(150000.0)):
            result = api.get_inventory_value()
            assert result == 150000.0

    def test_get_revenue(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse(500000.0)):
            result = api.get_revenue()
            assert result == 500000.0

    def test_connection_error(self, api):
        with patch.object(api.session, 'request', side_effect=requests.exceptions.ConnectionError):
            with pytest.raises(Exception, match="Не удалось подключиться к серверу"):
                api.get_products()

    def test_timeout_error(self, api):
        with patch.object(api.session, 'request', side_effect=requests.exceptions.Timeout):
            with pytest.raises(Exception, match="Превышено время ожидания"):
                api.get_products()

    def test_http_error_with_message(self, api):
        resp = MockResponse({"message": "Товар не найден"}, status_code=404)
        with patch.object(api.session, 'request', return_value=resp):
            with pytest.raises(Exception, match="Товар не найден"):
                api.get_product(999)

    def test_create_client(self, api):
        with patch.object(api.session, 'request', return_value=MockResponse({"id": 1, "fullName": "Клиент"})):
            result = api.create_client(full_name="Клиент", phone="+7-999")
            assert result["id"] == 1
