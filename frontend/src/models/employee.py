"""
Модель данных для сотрудника
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Employee:
    """Модель сотрудника"""
    
    id: int
    full_name: str
    position: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    login: Optional[str] = None
    access_level: str = "seller"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Employee':
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
            position=data.get('position'),
            phone_number=data.get('phoneNumber'),
            email=data.get('email'),
            login=data.get('login'),
            access_level=data.get('accessLevel', 'seller'),
            is_active=data.get('isActive', True),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь"""
        result = {
            'id': self.id,
            'fullName': self.full_name,
            'position': self.position,
            'phoneNumber': self.phone_number,
            'email': self.email,
            'login': self.login,
            'accessLevel': self.access_level,
            'isActive': self.is_active
        }
        
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        
        if self.updated_at:
            result['updatedAt'] = self.updated_at.isoformat()
        
        return result
    
    def validate(self, existing_emails: list[str] | None = None) -> list[str]:
        """Проверка: ФИО без цифр, уровень доступа, телефон, email, уникальность email."""
        from ..utils.validation import (
            require_access_level, require_person_name, require_phone, require_email,
            require_unique, ValidationError,
        )
        errors: list[str] = []
        try:
            require_person_name(self.full_name)
        except ValidationError as e:
            errors.append(str(e))
        try:
            require_access_level(self.access_level)
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
                    require_unique(self.email, existing_emails, "Email сотрудника")
                except ValidationError as e:
                    errors.append(str(e))
        return errors

    @property
    def display_name(self) -> str:
        """Отображаемое имя сотрудника"""
        return self.full_name.strip()
    
    @property
    def access_level_display(self) -> str:
        """Отображаемое название уровня доступа"""
        access_levels = {
            'admin': 'Администратор',
            'manager': 'Менеджер',
            'seller': 'Продавец',
            'florist': 'Флорист',
            'warehouse': 'Кладовщик',
            'courier': 'Курьер'
        }
        return access_levels.get(self.access_level, self.access_level)
    
    @property
    def is_admin(self) -> bool:
        """Является ли администратором"""
        return self.access_level == 'admin'
    
    @property
    def is_manager(self) -> bool:
        """Является ли менеджером"""
        return self.access_level in ['admin', 'manager']
    
    @property
    def can_manage_products(self) -> bool:
        """Может ли управлять товарами"""
        return self.access_level in ['admin', 'manager', 'florist']
    
    @property
    def can_manage_inventory(self) -> bool:
        """Может ли управлять складом"""
        return self.access_level in ['admin', 'manager', 'warehouse']
    
    @property
    def can_manage_orders(self) -> bool:
        """Может ли управлять заказами"""
        return self.access_level in ['admin', 'manager', 'seller']
    
    def __str__(self) -> str:
        return f"Employee(id={self.id}, name='{self.full_name}', level='{self.access_level}')"
    
    def __repr__(self) -> str:
        return self.__str__()