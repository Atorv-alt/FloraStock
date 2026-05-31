"""
Диалог входа в систему
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from src.services.api_service import ApiService


class LoginDialog(QDialog):
    """Диалог входа в систему"""
    
    # Сигнал успешной авторизации
    login_successful = pyqtSignal(dict)
    
    def __init__(self, api_service: ApiService, parent=None):
        super().__init__(parent)
        
        self.api_service = api_service
        self.user_data = None
        
        # Настройка логгера
        self.logger = logging.getLogger(__name__)
        
        # Настройка диалога
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("🌸 Вход в систему")
        self.setFixedSize(500, 400)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.resize(500, 400)
        
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(50, 30, 50, 30)
        
        # Заголовок с иконкой цветка
        title_label = QLabel("🌸 FloraStock")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2e7d32;")
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Система управления складом цветов")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        main_layout.addWidget(subtitle_label)
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # Форма входа
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Поле логина
        login_label = QLabel("👤 Логин:")
        form_layout.addWidget(login_label)
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setMinimumHeight(40)
        self.login_input.setMinimumWidth(300)
        form_layout.addWidget(self.login_input)
        
        # Поле пароля
        password_label = QLabel("🔒 Пароль:")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setMinimumWidth(300)
        form_layout.addWidget(self.password_input)
        
        main_layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.login_button = QPushButton("✅ Войти")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.login)
        self.login_button.setMinimumHeight(40)
        self.login_button.setMinimumWidth(120)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("❌ Отмена")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setMinimumWidth(120)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Добавляем растягивающееся пространство внизу
        main_layout.addStretch()
        
        # Устанавливаем фокус на поле логина
        self.login_input.setFocus()
        
        # Подключаем Enter для входа
        self.login_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.login)
    
    def setup_styles(self):
        """Настройка стилей"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            
            QLabel {
                color: #333333;
                font-weight: bold;
            }
            
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #4CAF50;
                outline: none;
            }
            
            QPushButton {
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            
            QPushButton#login_button {
                background-color: #4CAF50;
                color: white;
            }
            
            QPushButton#login_button:hover {
                background-color: #388E3C;
            }
            
            QPushButton#login_button:pressed {
                background-color: #1B5E20;
            }
            
            QPushButton#cancel_button {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #ddd;
            }
            
            QPushButton#cancel_button:hover {
                background-color: #e0e0e0;
            }
        """)
        
        self.login_button.setObjectName("login_button")
        self.cancel_button.setObjectName("cancel_button")
    
    def login(self):
        """Выполнение входа"""
        login = self.login_input.text().strip()
        password = self.password_input.text()
        
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            self.login_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            self.password_input.setFocus()
            return
        
        try:
            # Блокируем интерфейс на время выполнения запроса
            self.login_button.setEnabled(False)
            self.login_button.setText("Вход...")
            
            # Выполняем запрос к API
            response = self.api_service.login(login, password)
            
            # Сохраняем данные пользователя
            self.user_data = response
            
            self.logger.info(f"Пользователь {login} успешно вошел в систему")
            
            # Отправляем сигнал успешной авторизации
            self.login_successful.emit(self.user_data)
            
            # Закрываем диалог с результатом Accept только при успешном входе
            self.accept()
            
        except Exception as e:
            self.logger.error(f"Ошибка входа: {e}")
            
            # Показываем сообщение об ошибке без подсказок
            if "Не удалось подключиться к серверу" in str(e):
                QMessageBox.critical(self, "Ошибка подключения", 
                    "Не удалось подключиться к серверу.\n\n"
                    "Проверьте, что бэкенд запущен.")
            else:
                QMessageBox.critical(self, "Ошибка входа", "Неверный логин или пароль")
            
            # Очищаем поле пароля и устанавливаем фокус
            self.password_input.clear()
            self.password_input.setFocus()
            
            # НЕ закрываем диалог при ошибке - позволяем пользователю попробовать снова
            
        finally:
            # Восстанавливаем кнопку
            self.login_button.setEnabled(True)
            self.login_button.setText("Войти")
    
    def get_user_data(self):
        """Получить данные пользователя"""
        return self.user_data