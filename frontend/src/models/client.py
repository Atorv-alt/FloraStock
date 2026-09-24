"""
Модель данных для клиента
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Client:
    """Модель клиента"""
    
    id: int
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Client':
        """Создание объекта из словаря"""
        created_at = None
        if data.get('createdAt'):
            created_at = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
        
        updated_at = None
        if data.get('updatedAt'):
            updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            full_name=data['fullName'],
            phone_number=data.get('phoneNumber'),
            email=data.get('email'),
            is_active=data.get('isActive', True),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь"""
        result = {
            'id': self.id,
            'fullName': self.full_name,
            'phoneNumber': self.phone_number,
            'email': self.email,
            'isActive': self.is_active
        }
        
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        
        if self.updated_at:
            result['updatedAt'] = self.updated_at.isoformat()
        
        return result
    
    def validate(self, existing_emails: list[str] | None = None) -> list[str]:
        """Проверка: ФИО без цифр, телефон +7XXXXXXXXXX, email, уникальность email."""
        from ..utils.validation import (
            require_person_name, require_phone, require_email, require_unique, ValidationError,
        )
        errors: list[str] = []
        try:
            require_person_name(self.full_name)
        except ValidationError as e:
            errors.append(str(e))
        if self.phone_number:
            try:
                require_phone(self.phone_number)
            except ValidationError as e:
                errors.append(str(e))
        if self.email:
            try:
                require_email(self.email)
            except ValidationError as e:
                errors.append(str(e))
            if existing_emails is not None:
                try:
                    require_unique(self.email, existing_emails, "Email клиента")
                except ValidationError as e:
                    errors.append(str(e))
        return errors

    @property
    def display_name(self) -> str:
        """Отображаемое имя клиента"""
        return self.full_name.strip()
    
    @property
    def contact_info(self) -> str:
        """Контактная информация"""
        contacts = []
        if self.phone_number:
            contacts.append(f"Телефон: {self.phone_number}")
        if self.email:
            contacts.append(f"Email: {self.email}")
        return " | ".join(contacts) if contacts else "Нет контактных данных"
    
    def __str__(self) -> str:
        return f"Client(id={self.id}, name='{self.full_name}')"
    
    def __repr__(self) -> str:
        return self.__str__()