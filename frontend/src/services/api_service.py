"""
Сервис для взаимодействия с API бэкенда
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from ..utils.config import Config


def _to_jsonable(value):
    """Рекурсивно приводит date/datetime/Decimal к JSON-совместимым типам."""
    import datetime
    from decimal import Decimal
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
            return [_to_jsonable(v) for v in value]
    to_py_date = getattr(value, 'toPyDate', None)
    if callable(to_py_date):
        try:
            return to_py_date().isoformat()
        except Exception:
            return str(value)
    return value


class ApiService:
    """Класс для работы с API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.config = Config()
        self.session = requests.Session()
        self.token = None
        
        # Настройка логгера
        self.logger = logging.getLogger(__name__)
        
        # Установка заголовков по умолчанию
        self.session.headers.update(self.config.api_headers)
        
        # Установка таймаутов
        self.session.timeout = self.config.api_timeout
    
    def set_token(self, token: str):
        """Установка токена аутентификации"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def clear_token(self):
        """Очистка токена аутентификации"""
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполнение HTTP запроса"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        # requests.Session не имеет атрибута timeout — передаём явно в каждый запрос
        kwargs.setdefault('timeout', self.config.api_timeout)
        # date/datetime из виджетов (QDateEdit.toPyDate()) в ISO-строки,
        # иначе json.dumps упадёт с "Object of type date is not JSON serializable"
        if 'json' in kwargs and kwargs['json'] is not None:
            kwargs['json'] = _to_jsonable(kwargs['json'])
        
        try:
            self.logger.debug(f"{method.upper()} {url}")
            
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except Timeout:
            self.logger.error(f"Таймаут при запросе к {url}")
            raise Exception("Превышено время ожидания ответа от сервера")
            
        except ConnectionError:
            self.logger.error(f"Ошибка подключения к {url}")
            raise Exception("Не удалось подключиться к серверу")
            
        except RequestException as e:
            self.logger.error(f"Ошибка при запросе к {url}: {e}")
            if e.response is not None and e.response.content:
                try:
                    error_data = e.response.json()
                    message = error_data.get('message', f'HTTP {e.response.status_code}')
                except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                    try:
                        raw = e.response.content.decode('utf-8', errors='replace')
                    except Exception:
                        raw = ''
                    message = f'HTTP {e.response.status_code}: {raw[:200]}' if raw else f'HTTP {e.response.status_code}'
                raise Exception(message)
            raise Exception(f"Ошибка запроса: {e}")

        except (json.JSONDecodeError, UnicodeDecodeError):
            self.logger.error(f"Ошибка декодирования JSON из ответа {url}")
            raise Exception("Неверный формат ответа от сервера")
    
    # Методы аутентификации
    def login(self, login: str, password: str) -> Dict[str, Any]:
        """Вход в систему"""
        data = {
            'login': login,
            'password': password
        }
        response = self._make_request('POST', '/auth/login', json=data)
        if not isinstance(response, dict) or not response.get('token'):
            raise Exception("Неверный ответ сервера при входе")
        self.set_token(response['token'])
        return response
    
    def logout(self):
        """Выход из системы"""
        self.clear_token()
    
    def get_current_user(self) -> Dict[str, Any]:
        """Получение информации о текущем пользователе"""
        return self._make_request('GET', '/auth/me')
    
    def change_password(self, current_password: str, new_password: str) -> Dict[str, Any]:
        """Изменение пароля"""
        data = {
            'currentPassword': current_password,
            'newPassword': new_password
        }
        return self._make_request('POST', '/auth/change-password', json=data)
    
    # Методы работы с категориями
    def get_categories(self) -> List[Dict[str, Any]]:
        """Получение списка категорий"""
        response = self._make_request('GET', '/categories')
        return response if isinstance(response, list) else []
    
    def get_category(self, category_id: int) -> Dict[str, Any]:
        """Получение категории по ID"""
        return self._make_request('GET', f'/categories/{category_id}')
    
    def create_category(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Создание категории"""
        data = {
            'name': name,
            'description': description
        }
        return self._make_request('POST', '/categories', json=data)
    
    def update_category(self, category_id: int, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Обновление категории"""
        data = {
            'name': name,
            'description': description
        }
        return self._make_request('PUT', f'/categories/{category_id}', json=data)
    
    def delete_category(self, category_id: int) -> bool:
        """Удаление категории"""
        try:
            self._make_request('DELETE', f'/categories/{category_id}')
            return True
        except Exception:
            return False
    
    # Методы работы с товарами
    def get_products(self) -> List[Dict[str, Any]]:
        """Получение списка товаров"""
        response = self._make_request('GET', '/products')
        return response if isinstance(response, list) else []
    
    def get_active_products(self) -> List[Dict[str, Any]]:
        """Получение списка активных товаров"""
        response = self._make_request('GET', '/products/active')
        return response if isinstance(response, list) else []
    
    def get_products_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """Получение товаров по категории"""
        response = self._make_request('GET', f'/products/category/{category_id}')
        return response if isinstance(response, list) else []
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Получение товара по ID"""
        return self._make_request('GET', f'/products/{product_id}')
    
    def create_product(self, **kwargs) -> Dict[str, Any]:
        """Создание товара"""
        return self._make_request('POST', '/products', json=kwargs)
    
    def update_product(self, product_id: int, **kwargs) -> Dict[str, Any]:
        """Обновление товара"""
        return self._make_request('PUT', f'/products/{product_id}', json=kwargs)
    
    def delete_product(self, product_id: int) -> bool:
        """Удаление товара"""
        try:
            self._make_request('DELETE', f'/products/{product_id}')
            return True
        except Exception:
            return False
    
    def get_low_stock_products(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Получение товаров с низким остатком"""
        response = self._make_request('GET', f'/products/low-stock?threshold={threshold}')
        return response if isinstance(response, list) else []
    
    def get_inventory_value(self) -> float:
        """Получение стоимости склада"""
        response = self._make_request('GET', '/products/inventory-value')
        try:
            return float(response)
        except (TypeError, ValueError):
            return 0.0
    
    # Методы работы с клиентами
    def get_clients(self) -> List[Dict[str, Any]]:
        """Получение списка клиентов"""
        response = self._make_request('GET', '/clients')
        return response if isinstance(response, list) else []
    
    # Методы работы с сотрудниками
    def get_employees(self) -> List[Dict[str, Any]]:
        """Получение списка сотрудников"""
        response = self._make_request('GET', '/employees')
        return response if isinstance(response, list) else []
    
    def get_employee(self, employee_id: int) -> Dict[str, Any]:
        """Получение сотрудника по ID"""
        return self._make_request('GET', f'/employees/{employee_id}')
    
    def create_employee(self, **kwargs) -> Dict[str, Any]:
        """Создание сотрудника"""
        return self._make_request('POST', '/employees', json=kwargs)
    
    def update_employee(self, employee_id: int, **kwargs) -> Dict[str, Any]:
        """Обновление сотрудника"""
        return self._make_request('PUT', f'/employees/{employee_id}', json=kwargs)
    
    def delete_employee(self, employee_id: int) -> bool:
        """Удаление сотрудника"""
        try:
            self._make_request('DELETE', f'/employees/{employee_id}')
            return True
        except Exception:
            return False
    
    def get_active_clients(self) -> List[Dict[str, Any]]:
        """Получение списка активных клиентов"""
        response = self._make_request('GET', '/clients/active')
        return response if isinstance(response, list) else []
    
    def get_client(self, client_id: int) -> Dict[str, Any]:
        """Получение клиента по ID"""
        return self._make_request('GET', f'/clients/{client_id}')
    
    def search_client_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Поиск клиента по номеру телефона"""
        try:
            return self._make_request('GET', f'/clients/search/phone/{phone}')
        except Exception:
            return None
    
    def search_client_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Поиск клиента по email"""
        try:
            return self._make_request('GET', f'/clients/search/email/{email}')
        except Exception:
            return None
    
    def create_client(self, full_name: str, phone: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
        """Создание клиента"""
        data = {
            'fullName': full_name,
            'phoneNumber': phone,
            'email': email
        }
        return self._make_request('POST', '/clients', json=data)
    
    def update_client(self, client_id: int, **kwargs) -> Dict[str, Any]:
        """Обновление клиента"""
        return self._make_request('PUT', f'/clients/{client_id}', json=kwargs)
    
    def delete_client(self, client_id: int) -> bool:
        """Удаление клиента"""
        try:
            self._make_request('DELETE', f'/clients/{client_id}')
            return True
        except Exception:
            return False
    
    # Методы работы с заказами
    def get_orders(self) -> List[Dict[str, Any]]:
        """Получение списка заказов"""
        response = self._make_request('GET', '/orders')
        return response if isinstance(response, list) else []
    
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Получение заказа по ID"""
        return self._make_request('GET', f'/orders/{order_id}')
    
    def get_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Получение заказов по статусу"""
        response = self._make_request('GET', f'/orders/status/{status}')
        return response if isinstance(response, list) else []
    
    def get_orders_by_client(self, client_id: int) -> List[Dict[str, Any]]:
        """Получение заказов клиента"""
        response = self._make_request('GET', f'/orders/client/{client_id}')
        return response if isinstance(response, list) else []
    
    def create_order(self, **kwargs) -> Dict[str, Any]:
        """Создание заказа"""
        return self._make_request('POST', '/orders', json=kwargs)
    
    def update_order(self, order_id: int, **kwargs) -> Dict[str, Any]:
        """Обновление заказа"""
        return self._make_request('PUT', f'/orders/{order_id}', json=kwargs)
    
    def delete_order(self, order_id: int) -> bool:
        """Удаление заказа"""
        try:
            self._make_request('DELETE', f'/orders/{order_id}')
            return True
        except Exception:
            return False
    
    def get_revenue(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        """Получение выручки"""
        params = {}
        if start_date:
            params['startDate'] = start_date.isoformat()
        if end_date:
            params['endDate'] = end_date.isoformat()
        
        response = self._make_request('GET', '/orders/revenue', params=params)
        try:
            return float(response)
        except (TypeError, ValueError):
            return 0.0
    
    # Методы работы со складом
    def get_inventory(self) -> List[Dict[str, Any]]:
        """Получение складских остатков"""
        response = self._make_request('GET', '/inventory')
        return response if isinstance(response, list) else []
    
    def get_inventory_by_product(self, product_id: int) -> List[Dict[str, Any]]:
        """Получение остатков по товару"""
        response = self._make_request('GET', f'/inventory/product/{product_id}')
        return response if isinstance(response, list) else []
    
    def get_low_stock_inventory(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Получение товаров с низким остатком на складе"""
        response = self._make_request('GET', f'/inventory/low-stock?threshold={threshold}')
        return response if isinstance(response, list) else []
    
    def get_expiring_inventory(self, days_threshold: int = 7) -> List[Dict[str, Any]]:
        """Получение товаров с истекающим сроком годности"""
        response = self._make_request('GET', f'/inventory/expiring-soon?daysThreshold={days_threshold}')
        return response if isinstance(response, list) else []
    
    def create_inventory(self, **kwargs) -> Dict[str, Any]:
        """Создание складской позиции"""
        return self._make_request('POST', '/inventory', json=kwargs)
    
    def update_inventory(self, inventory_id: int, **kwargs) -> Dict[str, Any]:
        """Обновление складской позиции"""
        return self._make_request('PUT', f'/inventory/{inventory_id}', json=kwargs)
    
    def delete_inventory(self, inventory_id: int) -> bool:
        """Удаление складской позиции"""
        try:
            self._make_request('DELETE', f'/inventory/{inventory_id}')
            return True
        except Exception:
            return False
    
    def update_inventory_quantity(self, inventory_id: int, quantity: int) -> bool:
        """Обновление количества на складе"""
        try:
            self._make_request('PUT', f'/inventory/{inventory_id}/quantity', 
                             json={'quantity': quantity})
            return True
        except Exception:
            return False
    
    def transfer_stock(self, from_id: int, to_id: int, quantity: int) -> bool:
        """Перенос запасов между позициями"""
        try:
            self._make_request('POST', '/inventory/transfer', 
                             json={'fromId': from_id, 'toId': to_id, 'quantity': quantity})
            return True
        except Exception:
            return False
    
    # Методы работы с партиями
    def get_batches(self) -> List[Dict[str, Any]]:
        """Получение списка партий"""
        response = self._make_request('GET', '/batches')
        return response if isinstance(response, list) else []
    
    def get_batch(self, batch_id: int) -> Dict[str, Any]:
        """Получение партии по ID"""
        return self._make_request('GET', f'/batches/{batch_id}')
    
    def get_total_inventory_value(self) -> float:
        """Получение общей стоимости склада"""
        response = self._make_request('GET', '/inventory/total-value')
        try:
            return float(response)
        except (TypeError, ValueError):
            return 0.0
    
    # Методы работы с поставщиками
    def get_suppliers(self) -> List[Dict[str, Any]]:
        """Получение списка поставщиков"""
        response = self._make_request('GET', '/suppliers')
        return response if isinstance(response, list) else []
    
    def get_supplier(self, supplier_id: int) -> Dict[str, Any]:
        """Получение поставщика по ID"""
        return self._make_request('GET', f'/suppliers/{supplier_id}')
    
    def create_supplier(self, **kwargs) -> Dict[str, Any]:
        """Создание поставщика"""
        return self._make_request('POST', '/suppliers', json=kwargs)
    
    def update_supplier(self, supplier_id: int, **kwargs) -> Dict[str, Any]:
        """Обновление поставщика"""
        return self._make_request('PUT', f'/suppliers/{supplier_id}', json=kwargs)
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """Удаление поставщика"""
        try:
            self._make_request('DELETE', f'/suppliers/{supplier_id}')
            return True
        except Exception:
            return False
    
    # Методы работы с партиями
    def create_batch(self, **kwargs) -> Dict[str, Any]:
        """Создание партии"""
        return self._make_request('POST', '/batches', json=kwargs)
    
    def update_batch(self, batch_id: int, **kwargs) -> Dict[str, Any]:
        """Обновление партии"""
        return self._make_request('PUT', f'/batches/{batch_id}', json=kwargs)
    
    def delete_batch(self, batch_id: int) -> bool:
        """Удаление партии"""
        try:
            self._make_request('DELETE', f'/batches/{batch_id}')
            return True
        except Exception:
            return False