"""
Модель данных для товара
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal

from .category import Category


@dataclass
class Product:
    """Модель товара"""
    
    id: int
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    category: Optional[Category] = None
    unit: str = "шт"
    purchase_price: Decimal = Decimal('0.00')
    retail_price: Decimal = Decimal('0.00')
    shelf_life_days: int = 7
    color: Optional[str] = None
    stem_length_cm: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Создание объекта из словаря"""
        created_at = None
        if data.get('createdAt'):
            created_at = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
        
        updated_at = None
        if data.get('updatedAt'):
            updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
        
        category = None
        if data.get('category'):
            category = Category.from_dict(data['category'])
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            category_id=data.get('categoryId'),
            category=category,
            unit=data.get('unit', 'шт'),
            purchase_price=Decimal(str(data.get('purchasePrice', '0.00'))),
            retail_price=Decimal(str(data.get('retailPrice', '0.00'))),
            shelf_life_days=data.get('shelfLifeDays', 7),
            color=data.get('color'),
            stem_length_cm=data.get('stemLengthCm'),
            is_active=data.get('isActive', True),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь"""
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'categoryId': self.category_id,
            'unit': self.unit,
            'purchasePrice': float(self.purchase_price),
            'retailPrice': float(self.retail_price),
            'shelfLifeDays': self.shelf_life_days,
            'color': self.color,
            'stemLengthCm': self.stem_length_cm,
            'isActive': self.is_active
        }
        
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        
        if self.updated_at:
            result['updatedAt'] = self.updated_at.isoformat()
        
        return result
    
    @property
    def category_name(self) -> str:
        """Название категории"""
        return self.category.name if self.category else "Без категории"
    
    @property
    def margin_percentage(self) -> float:
        """Процент наценки"""
        if self.purchase_price == 0:
            return 0.0
        return float(((self.retail_price - self.purchase_price) / self.purchase_price) * 100)
    
    @property
    def margin_amount(self) -> Decimal:
        """Сумма наценки"""
        return self.retail_price - self.purchase_price
    
    def __str__(self) -> str:
        return f"Product(id={self.id}, name='{self.name}', price={self.retail_price})"
    
    def __repr__(self) -> str:
        return self.__str__()