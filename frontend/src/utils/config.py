"""
Конфигурация приложения
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Класс конфигурации приложения"""
    
    def __init__(self):
        self._load_settings()
        
        # Базовые пути
        self.app_dir = Path(__file__).parent.parent.parent
        self.resources_dir = self.app_dir / "resources"
        
        # API конфигурация
        self.api_base_url = self._get_config("API_BASE_URL", "http://localhost:5000/api")
        
        # База данных PostgreSQL
        self.db_host = self._get_config("DB_HOST", "localhost")
        self.db_port = self._get_config("DB_PORT", "5432")
        self.db_name = self._get_config("DB_NAME", "sclad")
        self.db_user = self._get_config("DB_USER", "postgres")
        self.db_password = self._get_config("DB_PASSWORD", "")
        
        # Настройки приложения
        self.app_name = "🌸 FloraStock"
        self.app_subtitle = "Система управления складом цветов"
        self.app_version = "1.0.0"
        
        # UI настройки
        self.window_width = 1200
        self.window_height = 800
        self.window_min_width = 800
        self.window_min_height = 600
        
        # Таймауты
        self.api_timeout = 30
        self.request_retry_count = 3
        
        # Логирование
        self.log_level = self._get_config("LOG_LEVEL", "INFO")
        self.log_file = self.app_dir / "logs" / "app.log"
        
        # Язык и локализация
        self.language = self._get_config("APP_LANGUAGE", "ru_RU")
        
        # Безопасность
        self.token_storage_key = "florastock_token"
        self.remember_user_key = "florastock_remember_user"
        
        self._create_directories()
    
    def _load_settings(self):
        """Загрузка настроек из файла"""
        self._settings = {}
        config_file = Path(__file__).parent.parent.parent / "config.ini"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            self._settings[key.strip()] = value.strip()
            except Exception:
                pass
    
    def _get_config(self, key: str, default: str) -> str:
        """Получить значение конфигурации"""
        if hasattr(self, '_settings') and key in self._settings:
            return self._settings[key]
        return os.getenv(key, default)
    
    def save_db_config(self, host: str, port: str, name: str, user: str, password: str,
                       api_base_url: Optional[str] = None):
        """Сохранение конфигурации БД (адрес API при этом не затирается)."""
        if api_base_url:
            self.api_base_url = api_base_url.rstrip('/')
        config_file = Path(__file__).parent.parent.parent / "config.ini"
        config_content = f"""# FloraStock Configuration
API_BASE_URL={self.api_base_url}
DB_HOST={host}
DB_PORT={port}
DB_NAME={name}
DB_USER={user}
DB_PASSWORD={password}
"""
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        self.db_host = host
        self.db_port = port
        self.db_name = name
        self.db_user = user
        self.db_password = password
    
    def _create_directories(self):
        """Создание необходимых директорий"""
        directories = [
            self.app_dir / "data",
            self.app_dir / "logs",
            self.resources_dir / "icons",
            self.resources_dir / "styles",
            self.resources_dir / "translations"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_development(self) -> bool:
        """Проверка режима разработки"""
        return os.getenv("ENVIRONMENT", "production").lower() == "development"
    
    @property
    def api_headers(self) -> dict:
        """Заголовки для API запросов"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_icon_path(self, icon_name: str) -> Optional[str]:
        """Получить путь к иконке"""
        icon_path = self.resources_dir / "icons" / icon_name
        return str(icon_path) if icon_path.exists() else None
    
    def get_style_path(self, style_name: str) -> Optional[str]:
        """Получить путь к файлу стилей"""
        style_path = self.resources_dir / "styles" / style_name
        return str(style_path) if style_path.exists() else None