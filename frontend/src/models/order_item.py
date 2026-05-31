"""
Модель данных для позиции заказа
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal

from .product import Product


@dataclass
class OrderItem:
    """Модель позиции заказа"""
    
    id: int
    order_id: int
    product_id: Optional[int] = None
    product: Optional[Product] = None
    quantity: int = 1
    unit_price: Decimal = Decimal('0.00')
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OrderItem':
        """Создание объекта из словаря"""
        created_at = None
        if data.get('createdAt'):
            created_at = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
        
        updated_at = None
        if data.get('updatedAt'):
            updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
        
        product = None
        if data.get('product'):
            product = Product.from_dict(data['product'])
        
        return cls(
            id=data['id'],
            order_id=data['orderId'],
            product_id=data.get('productId'),
            product=product,
            quantity=data.get('quantity', 1),
            unit_price=Decimal(str(data.get('unitPrice', '0.00'))),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь"""
        result = {
            'id': self.id,
            'orderId': self.order_id,
            'productId': self.product_id,
            'quantity': self.quantity,
            'unitPrice': float(self.unit_price)
        }
        
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        
        if self.updated_at:
            result['updatedAt'] = self.updated_at.isoformat()
        
        return result
    
    @property
    def product_name(self) -> str:
        """Название товара"""
        return self.product.name if self.product else f"Товар #{self.product_id}"
    
    @property
    def total_price(self) -> Decimal:
        """Общая стоимость позиции"""
        return self.quantity * self.unit_price
    
    @property
    def unit_name(self) -> str:
        """Единица измерения"""
        return self.product.unit if self.product else "шт"
    
    def __str__(self) -> str:
        return f"OrderItem(id={self.id}, product='{self.product_name}', quantity={self.quantity})"
    
    def __repr__(self) -> str:
        return self.__str__()