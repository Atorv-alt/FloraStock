"""
Модель данных для заказа
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from .client import Client
from .employee import Employee
from .order_item import OrderItem


@dataclass
class Order:
    """Модель заказа"""
    
    id: int
    order_number: str
    order_date: date
    status: str
    total_amount: Decimal
    client_id: Optional[int] = None
    client: Optional[Client] = None
    employee_id: Optional[int] = None
    employee: Optional[Employee] = None
    order_items: Optional[List[OrderItem]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """Создание объекта из словаря"""
        created_at = None
        if data.get('createdAt'):
            created_at = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
        
        updated_at = None
        if data.get('updatedAt'):
            updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
        
        order_date = None
        if data.get('orderDate'):
            order_date = datetime.fromisoformat(data['orderDate']).date()
        
        # Обработка клиента - может быть объектом или строкой
        client = None
        client_name = data.get('clientName', '')
        if data.get('client'):
            if isinstance(data['client'], dict):
                client = Client.from_dict(data['client'])
            else:
                client_name = str(data['client'])
        elif client_name:
            # Создаем клиента-заглушку с именем из API
            client = Client(id=data.get('clientId', 0), full_name=client_name)
        
        employee = None
        if data.get('employee'):
            if isinstance(data['employee'], dict):
                employee = Employee.from_dict(data['employee'])
            else:
                employee = Employee(id=data.get('employeeId', 0), full_name=str(data['employee']))
        
        order_items = None
        if data.get('orderItems'):
            order_items = [OrderItem.from_dict(item) for item in data['orderItems']]
        
        return cls(
            id=data['id'],
            order_number=data.get('orderNumber', ''),
            order_date=order_date or date.today(),
            status=data.get('status', 'Новый'),
            total_amount=Decimal(str(data.get('totalAmount', '0.00'))),
            client_id=data.get('clientId'),
            client=client,
            employee_id=data.get('employeeId'),
            employee=employee,
            order_items=order_items,
            is_active=data.get('isActive', True),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь"""
        result = {
            'id': self.id,
            'orderNumber': self.order_number,
            'orderDate': self.order_date.isoformat(),
            'status': self.status,
            'totalAmount': float(self.total_amount),
            'clientId': self.client_id,
            'employeeId': self.employee_id,
            'isActive': self.is_active
        }
        
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        
        if self.updated_at:
            result['updatedAt'] = self.updated_at.isoformat()
        
        return result
    
    @property
    def client_name(self) -> str:
        """Имя клиента"""
        if self.client:
            return self.client.full_name
        return "Не указан"
    
    @property
    def employee_name(self) -> str:
        """Имя сотрудника"""
        return self.employee.full_name if self.employee else "Не указан"
    
    @property
    def items_count(self) -> int:
        """Количество позиций в заказе"""
        return len(self.order_items) if self.order_items else 0
    
    @property
    def status_color(self) -> str:
        """Цвет статуса для отображения"""
        status_colors = {
            'Новый': '#2196F3',      # Синий
            'В обработке': '#FF9800', # Оранжевый
            'Готов к выдаче': '#4CAF50', # Зеленый
            'Выполнен': '#9C27B0',   # Фиолетовый
            'Отменен': '#F44336'      # Красный
        }
        return status_colors.get(self.status, '#757575')  # Серый по умолчанию
    
    @property
    def can_edit(self) -> bool:
        """Можно ли редактировать заказ"""
        return self.status in ['Новый', 'В обработке']
    
    @property
    def can_cancel(self) -> bool:
        """Можно ли отменить заказ"""
        return self.status in ['Новый', 'В обработке']
    
    def add_item(self, item: OrderItem):
        """Добавление позиции в заказ"""
        if self.order_items is None:
            self.order_items = []
        self.order_items.append(item)
        self._recalculate_total()
    
    def remove_item(self, product_id: int):
        """Удаление позиции из заказа"""
        if self.order_items:
            self.order_items = [item for item in self.order_items if item.product_id != product_id]
            self._recalculate_total()
    
    def _recalculate_total(self):
        """Пересчет общей суммы заказа"""
        if self.order_items:
            self.total_amount = sum(item.quantity * item.unit_price for item in self.order_items)
        else:
            self.total_amount = Decimal('0.00')
    
    def __str__(self) -> str:
        return f"Order(id={self.id}, number='{self.order_number}', status='{self.status}')"
    
    def __repr__(self) -> str:
        return self.__str__()