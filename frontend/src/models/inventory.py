"""
Модель данных для складской позиции
"""

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Optional
from decimal import Decimal

from .product import Product
from .batch import Batch


@dataclass
class Inventory:
    """Модель складской позиции"""
    
    id: int
    quantity: int
    receipt_date: date
    product_id: Optional[int] = None
    product: Optional[Product] = None
    batch_id: Optional[int] = None
    batch: Optional[Batch] = None
    storage_location: Optional[str] = None
    storage_temperature: Optional[str] = None
    humidity_level: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Inventory':
        """Создание объекта из словаря"""
        created_at = None
        if data.get('createdAt'):
            created_at = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
        
        updated_at = None
        if data.get('updatedAt'):
            updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
        
        receipt_date = None
        if data.get('receiptDate'):
            receipt_date = datetime.fromisoformat(data['receiptDate']).date()
        
        product = None
        if data.get('product'):
            product = Product.from_dict(data['product'])
        
        batch = None
        if data.get('batch'):
            batch = Batch.from_dict(data['batch'])
        
        return cls(
            id=data['id'],
            quantity=data.get('quantity', 0),
            receipt_date=receipt_date or date.today(),
            product_id=data.get('productId'),
            product=product,
            batch_id=data.get('batchId'),
            batch=batch,
            storage_location=data.get('storageLocation'),
            storage_temperature=data.get('storageTemperature'),
            humidity_level=data.get('humidityLevel'),
            is_active=data.get('isActive', True),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь"""
        result = {
            'id': self.id,
            'quantity': self.quantity,
            'receiptDate': self.receipt_date.isoformat(),
            'productId': self.product_id,
            'batchId': self.batch_id,
            'storageLocation': self.storage_location,
            'storageTemperature': self.storage_temperature,
            'humidityLevel': self.humidity_level,
            'isActive': self.is_active
        }
        
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        
        if self.updated_at:
            result['updatedAt'] = self.updated_at.isoformat()
        
        return result
    
    def validate(self) -> list[str]:
        """Проверка: количество на складе >= 0."""
        from ..utils.validation import require_non_negative_int, ValidationError
        errors: list[str] = []
        try:
            require_non_negative_int(self.quantity, "Количество на складе")
        except ValidationError as e:
            errors.append(str(e))
        return errors

    @property
    def product_name(self) -> str:
        """Название товара"""
        return self.product.name if self.product else f"Товар #{self.product_id}"
    
    @property
    def category_name(self) -> str:
        """Название категории"""
        if self.product and self.product.category:
            return self.product.category.name
        return "Без категории"
    
    @property
    def total_value(self) -> Decimal:
        """Общая стоимость позиции"""
        if self.product:
            return self.quantity * self.product.retail_price
        return Decimal('0.00')
    
    @property
    def days_in_stock(self) -> int:
        """Количество дней на складе"""
        return (date.today() - self.receipt_date).days
    
    @property
    def is_expiring_soon(self, days_threshold: int = 7) -> bool:
        """Проверка, истекает ли срок годности скоро"""
        if not self.product or self.product.shelf_life_days <= 0:
            return False
        expiry_date = self.receipt_date + timedelta(days=self.product.shelf_life_days)
        return (expiry_date - date.today()).days <= days_threshold
    
    @property
    def is_expired(self) -> bool:
        """Проверка, истек ли срок годности"""
        if not self.product or self.product.shelf_life_days <= 0:
            return False
        expiry_date = self.receipt_date + timedelta(days=self.product.shelf_life_days)
        return expiry_date < date.today()
    
    @property
    def expiry_date(self) -> Optional[date]:
        """Дата истечения срока годности"""
        if not self.product or self.product.shelf_life_days <= 0:
            return None
        return self.receipt_date + timedelta(days=self.product.shelf_life_days)
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Дней до истечения срока годности"""
        expiry = self.expiry_date
        if expiry:
            return (expiry - date.today()).days
        return None
    
    @property
    def is_low_stock(self, threshold: int = 10) -> bool:
        """Проверка, является ли остаток низким"""
        return self.quantity <= threshold
    
    @property
    def stock_status(self) -> str:
        """Статус остатка"""
        if self.quantity == 0:
            return "Отсутствует"
        elif self.quantity <= 5:
            return "Критически низкий"
        elif self.quantity <= 10:
            return "Низкий"
        elif self.quantity <= 50:
            return "Нормальный"
        else:
            return "Высокий"
    
    @property
    def stock_status_color(self) -> str:
        """Цвет статуса остатка"""
        if self.quantity == 0:
            return "#F44336"  # Красный
        elif self.quantity <= 5:
            return "#FF9800"  # Оранжевый
        elif self.quantity <= 10:
            return "#FFC107"  # Желтый
        elif self.quantity <= 50:
            return "#4CAF50"  # Зеленый
        else:
            return "#2196F3"  # Синий
    
    def __str__(self) -> str:
        return f"Inventory(id={self.id}, product='{self.product_name}', quantity={self.quantity})"
    
    def __repr__(self) -> str:
        return self.__str__()