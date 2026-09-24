#!/usr/bin/env python3
"""
Главный файл приложения Business Shop Frontend
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QTranslator, QLocale
from PyQt6.QtGui import QIcon

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.main_window import MainWindow
from src.services.api_service import ApiService
from src.utils.config import Config


class BusinessShopApp:
    """Основной класс приложения"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.api_service = None
        self.config = None
        
    def initialize(self):
        """Инициализация приложения"""
        # Создаем приложение Qt
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Business Shop Management System")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Business Shop")
        
        # Устанавливаем иконку приложения
        icon_path = Path(__file__).parent.parent / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))
        
        # Загружаем конфигурацию
        self.config = Config()
        
        # Инициализируем API сервис
        self.api_service = ApiService(self.config.api_base_url)
        
        # Устанавливаем перевод (если нужно)
        self.setup_translations()
        
        # Создаем главное окно
        self.main_window = MainWindow(self.api_service, self.config)
        
    def setup_translations(self):
        """Настройка переводов"""
        translator = QTranslator()
        locale = QLocale.system().name()
        
        # Загружаем перевод если он существует
        translations_path = Path(__file__).parent.parent / "resources" / "translations"
        if translator.load(f"app_{locale}", str(translations_path)):
            self.app.installTranslator(translator)
    
    def run(self):
        """Запуск приложения"""
        if not self.app:
            self.initialize()
        
        # Главное окно само показывает диалог входа в __init__
        # и отображается только после успешной авторизации
        return self.app.exec()


def main():
    """Точка входа в приложение"""
    try:
        app = BusinessShopApp()
        return app.run()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())