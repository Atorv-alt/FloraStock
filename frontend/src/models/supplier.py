"""
Модель данных для поставщика
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Supplier:
    """Модель поставщика"""
    
    id: int
    name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    details: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Supplier':
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
            phone_number=data.get('phoneNumber'),
            email=data.get('email'),
            details=data.get('details'),
            address=data.get('address'),
            is_active=data.get('isActive', True),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь"""
        result = {
            'id': self.id,
            'name': self.name,
            'phoneNumber': self.phone_number,
            'email': self.email,
            'details': self.details,
            'address': self.address,
            'isActive': self.is_active
        }
        
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        
        if self.updated_at:
            result['updatedAt'] = self.updated_at.isoformat()
        
        return result
    
    @property
    def display_name(self) -> str:
        """Отображаемое название поставщика"""
        return self.name.strip()

    def validate(self) -> list[str]:
        """Проверка: непустое название, телефон +7XXXXXXXXXX, email стандартного формата."""
        from ..utils.validation import ValidationError, require_name, validate_supplier_dict
        errors = validate_supplier_dict({
            "phone_number": self.phone_number,
            "email": self.email,
        })
        try:
            require_name(self.name, "Название поставщика")
        except ValidationError as e:
            errors.insert(0, str(e))
        return errors
    
    @property
    def contact_info(self) -> str:
        """Контактная информация"""
        contacts = []
        if self.phone_number:
            contacts.append(f"Телефон: {self.phone_number}")
        if self.email:
            contacts.append(f"Email: {self.email}")
        return " | ".join(contacts) if contacts else "Нет контактных данных"
    
    @property
    def full_address(self) -> str:
        """Полный адрес"""
        return self.address or "Адрес не указан"
    
    def __str__(self) -> str:
        return f"Supplier(id={self.id}, name='{self.name}')"
    
    def __repr__(self) -> str:
        return self.__str__()