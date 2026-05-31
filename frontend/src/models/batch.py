"""
Модель данных для партии поставки
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from .supplier import Supplier


@dataclass
class Batch:
    """Модель партии поставки"""
    
    id: int
    quantity: int
    cost_price: Decimal
    delivery_date: Optional[date] = None
    invoice_number: Optional[str] = None
    supplier_id: Optional[int] = None
    supplier: Optional[Supplier] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Batch':
        """Создание объекта из словаря"""
        created_at = None
        if data.get('createdAt'):
            created_at = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
        
        updated_at = None
        if data.get('updatedAt'):
            updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
        
        delivery_date = None
        if data.get('deliveryDate'):
            delivery_date = datetime.fromisoformat(data['deliveryDate']).date()
        
        supplier = None
        if data.get('supplier'):
            supplier = Supplier.from_dict(data['supplier'])
        
        return cls(
            id=data['id'],
            quantity=data.get('quantity', 0),
            cost_price=Decimal(str(data.get('costPrice', '0.00'))),
            delivery_date=delivery_date,
            invoice_number=data.get('invoiceNumber'),
            supplier_id=data.get('supplierId'),
            supplier=supplier,
            is_active=data.get('isActive', True),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь"""
        result = {
            'id': self.id,
            'quantity': self.quantity,
            'costPrice': float(self.cost_price),
            'isActive': self.is_active
        }
        
        if self.delivery_date:
            result['deliveryDate'] = self.delivery_date.isoformat()
        
        if self.invoice_number:
            result['invoiceNumber'] = self.invoice_number
        
        if self.supplier_id:
            result['supplierId'] = self.supplier_id
        
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        
        if self.updated_at:
            result['updatedAt'] = self.updated_at.isoformat()
        
        return result
    
    @property
    def supplier_name(self) -> str:
        """Название поставщика"""
        return self.supplier.name if self.supplier else "Не указан"
    
    @property
    def unit_cost(self) -> Decimal:
        """Стоимость единицы товара"""
        if self.quantity > 0:
            return self.cost_price / self.quantity
        return Decimal('0.00')
    
    @property
    def days_since_delivery(self) -> Optional[int]:
        """Дней с момента поставки"""
        if self.delivery_date:
            return (date.today() - self.delivery_date).days
        return None
    
    @property
    def delivery_status(self) -> str:
        """Статус поставки"""
        if not self.delivery_date:
            return "Ожидается"
        elif self.delivery_date > date.today():
            return "Запланирована"
        elif self.delivery_date == date.today():
            return "Сегодня"
        else:
            days_ago = self.days_since_delivery
            if days_ago == 1:
                return "Вчера"
            elif days_ago <= 7:
                return f"{days_ago} дней назад"
            else:
                return f"{days_ago} дней назад"
    
    def __str__(self) -> str:
        return f"Batch(id={self.id}, quantity={self.quantity}, cost={self.cost_price})"
    
    def __repr__(self) -> str:
        return self.__str__()