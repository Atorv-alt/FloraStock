"""
Модель данных для категории
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Category:
    """Модель категории товаров"""
    
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Category':
        """Создание объекта из словаря"""
        created_at = None
        if data.get('createdAt'):
            created_at = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
        
        updated_at = None
        if data.get('updatedAt'):
            updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь"""
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        
        if self.updated_at:
            result['updatedAt'] = self.updated_at.isoformat()
        
        return result
    
    def validate(self, existing_names: list[str] | None = None) -> list[str]:
        """Проверка: непустое наименование + длина + уникальность."""
        from ..utils.validation import require_name, require_unique, ValidationError
        errors: list[str] = []
        try:
            require_name(self.name, "Наименование категории")
        except ValidationError as e:
            errors.append(str(e))
            return errors
        if existing_names is not None:
            try:
                require_unique(self.name, existing_names, "Наименование категории")
            except ValidationError as e:
                errors.append(str(e))
        return errors

    def __str__(self) -> str:
        return f"Category(id={self.id}, name='{self.name}')"
    
    def __repr__(self) -> str:
        return self.__str__()