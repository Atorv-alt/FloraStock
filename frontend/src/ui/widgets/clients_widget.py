"""
Виджет управления клиентами
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, 
    QLineEdit, QCheckBox, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.services.api_service import ApiService
from src.models import Client


def _check_duplicate(exc, field_name, field_value):
    from src.utils.validation import format_duplicate_error
    return format_duplicate_error(exc, field_name, field_value)


class ClientsWidget(QWidget):
    """Виджет управления клиентами"""
    
    # Сигнал обновления данных
    data_updated = pyqtSignal()
    
    def __init__(self, api_service: ApiService):
        super().__init__()
        
        self.api_service = api_service
        self.clients = []
        
        # Настройка логгера
        self.logger = logging.getLogger(__name__)
        
        # Инициализация UI
        self.setup_ui()
        self.setup_styles()
        
        # Подключаем сигналы
        self.connect_signals()
        
        # НЕ загружаем начальные данные - будем грузить только после входа
        # self.refresh_data()  # Будет вызвано после авторизации
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Адаптивная панель управления
        header_layout = QHBoxLayout()
        
        # Заголовок с иконкой и адаптивным размером
        title_label = QLabel("👥 Управление клиентами")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Адаптивные кнопки действий
        self.add_client_btn = QPushButton("➕ Добавить")
        self.add_client_btn.setMinimumWidth(80)
        self.add_client_btn.clicked.connect(self.add_client)
        header_layout.addWidget(self.add_client_btn)
        
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumWidth(80)
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Адаптивная панель поиска
        search_layout = QHBoxLayout()
        
        search_label = QLabel("🔍 Поиск:")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите ФИО, телефон или email...")
        self.search_input.setMinimumWidth(200)
        self.search_input.textChanged.connect(self.filter_clients)
        search_layout.addWidget(self.search_input)
        
        search_layout.addStretch()  # Растягиваем для адаптивности
        main_layout.addLayout(search_layout)
        
        # Адаптивная таблица клиентов
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(5)
        self.clients_table.setHorizontalHeaderLabels([
            "ID", "ФИО", "Телефон", "Email", "Действия"
        ])
        
        # Адаптивная настройка таблицы
        header = self.clients_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # ФИО растягивается
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Телефон
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Действия - фиксированная ширина
        header.resizeSection(4, 100)  # Фиксированная ширина для кнопок
        
        self.clients_table.setAlternatingRowColors(True)
        self.clients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.clients_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.clients_table.setMinimumHeight(300)  # Минимальная высота для адаптивности
        
        main_layout.addWidget(self.clients_table)
        
        # Информационная панель
        info_layout = QHBoxLayout()
        
        self.info_label = QLabel("Загрузка данных...")
        info_layout.addWidget(self.info_label)
        
        info_layout.addStretch()
        
        self.total_label = QLabel("Всего: 0")
        info_layout.addWidget(self.total_label)
        
        main_layout.addLayout(info_layout)
    
    def setup_styles(self):
        """Настройка стилей"""
        self.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: bold;
            }
            
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            
            QPushButton {
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                background-color: #2196F3;
                color: #FFFFFF;
            }
            
            QPushButton:hover {
                background-color: #1976D2;
                color: #FFFFFF;
            }
            
            QPushButton:pressed {
                background-color: #0D47A1;
                color: #FFFFFF;
            }
            
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
            
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f5f5f5;
                color: #333333;
            }
            
            QTableWidget::item {
                padding: 5px;
                color: #333333;
            }
            
            QTableWidget::item:selected {
                background-color: #c8e6c9;
                color: #333333;
            }
            
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
    
    def connect_signals(self):
        """Подключение сигналов"""
        self.data_updated.connect(self.update_table)
        self.clients_table.doubleClicked.connect(self.edit_client)
    
    def refresh_data(self):
        """Обновить данные"""
        try:
            # Проверяем, есть ли токен авторизации
            if not self.api_service.token:
                self.logger.info("Пропуск обновления данных - пользователь не авторизован")
                return
            
            self.info_label.setText("Загрузка данных...")
            
            # Загружаем клиентов
            self.clients = [Client.from_dict(c) for c in self.api_service.get_clients()]
            
            # Применяем фильтр
            self.filter_clients()
            
            self.info_label.setText("Данные загружены")
            self.logger.info(f"Загружено {len(self.clients)} клиентов")
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке клиентов: {e}")
            self.info_label.setText(f"Ошибка: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить клиентов: {e}")
    
    def filter_clients(self):
        """Отфильтровать клиентов"""
        try:
            search_text = self.search_input.text().lower()
            
            filtered_clients = []
            
            for client in self.clients:
                # Фильтр по поиску
                if not search_text or (
                    search_text in client.full_name.lower() or
                    (client.phone_number and search_text in client.phone_number.lower()) or
                    (client.email and search_text in client.email.lower())
                ):
                    filtered_clients.append(client)
            
            # Обновляем таблицу
            self.update_table_with_clients(filtered_clients)
            
            # Обновляем счетчик
            self.total_label.setText(f"Всего: {len(filtered_clients)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при фильтрации клиентов: {e}")
    
    def update_table_with_clients(self, clients):
        """Обновить таблицу с указанными клиентами"""
        self.clients_table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            # ID
            self.clients_table.setItem(row, 0, QTableWidgetItem(str(client.id)))
            
            # ФИО
            name_item = QTableWidgetItem(client.full_name)
            if not client.is_active:
                name_item.setForeground(Qt.GlobalColor.gray)
            self.clients_table.setItem(row, 1, name_item)
            
            # Телефон
            phone_text = client.phone_number or "-"
            self.clients_table.setItem(row, 2, QTableWidgetItem(phone_text))
            
            # Email
            email_text = client.email or "-"
            self.clients_table.setItem(row, 3, QTableWidgetItem(email_text))
            
            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setFixedSize(28, 24)
            edit_btn.clicked.connect(lambda checked, c=client: self.edit_client_by_object(c))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Удалить")
            delete_btn.setFixedSize(28, 24)
            delete_btn.clicked.connect(lambda checked, c=client: self.delete_client_by_object(c))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.clients_table.setCellWidget(row, 4, actions_widget)
    
    def update_table(self):
        """Обновить таблицу"""
        self.filter_clients()
    
    def add_client(self):
        """Добавить клиента"""
        dialog = ClientDialog(self.api_service, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def edit_client(self, index):
        """Редактировать клиента по индексу таблицы"""
        row = index.row()
        _cell = self.clients_table.item(row, 0)
        try:
            client_id = int(_cell.text()) if _cell is not None else -1
        except (TypeError, ValueError):
            client_id = -1
        if client_id < 0:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить ID записи")
            return
        self.edit_client_by_id(client_id)
    
    def edit_client_by_id(self, client_id):
        """Редактировать клиента по ID"""
        try:
            client_data = self.api_service.get_client(client_id)
            client = Client.from_dict(client_data)
            self.edit_client_by_object(client)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить клиента: {e}")
    
    def edit_client_by_object(self, client):
        """Редактировать клиента"""
        dialog = ClientDialog(self.api_service, self, client)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def delete_client_by_object(self, client):
        """Удалить клиента"""
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить клиента '{client.full_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_service.delete_client(client.id)
                QMessageBox.information(self, "Успех", "Клиент успешно удален")
                self.refresh_data()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить клиента: {e}")


class ClientDialog(QDialog):
    """Диалог добавления/редактирования клиента"""
    
    def __init__(self, api_service: ApiService, parent=None, client: Client = None):
        super().__init__(parent)
        
        self.api_service = api_service
        self.client = client
        
        self.setup_ui()
        self.setup_styles()
        
        if client:
            self.load_client_data()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Добавление клиента" if not self.client else "Редактирование клиента")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        # ФИО
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Введите ФИО клиента")
        form_layout.addRow("ФИО *:", self.full_name_input)
        
        # Телефон
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Введите номер телефона")
        form_layout.addRow("Телефон:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите email")
        form_layout.addRow("Email:", self.email_input)
        
        # Статус
        self.active_checkbox = QCheckBox("Активен")
        self.active_checkbox.setChecked(True)
        form_layout.addRow("Статус:", self.active_checkbox)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_client)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def setup_styles(self):
        """Настройка стилей"""
        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)
    
    def load_client_data(self):
        """Загрузить данные клиента"""
        if self.client:
            self.full_name_input.setText(self.client.full_name)
            self.phone_input.setText(self.client.phone_number or "")
            self.email_input.setText(self.client.email or "")
            self.active_checkbox.setChecked(self.client.is_active)
    
    def reset_field_styles(self):
        default = "padding: 5px; border: 1px solid #ddd; border-radius: 3px;"
        for inp in [self.full_name_input, self.phone_input, self.email_input]:
            inp.setStyleSheet(default)

    def save_client(self):
        """Сохранить клиента"""
        errors = []
        self.reset_field_styles()

        full_name = self.full_name_input.text().strip()
        if not full_name:
            errors.append("❌ Поле «ФИО» обязательно для заполнения.")
            self.full_name_input.setStyleSheet(self.full_name_input.styleSheet() + "background-color: #ffe6e6;")

        from src.utils.validation import require_email, require_person_name, require_phone
        if full_name:
            try:
                require_person_name(full_name)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.full_name_input.setStyleSheet(self.full_name_input.styleSheet() + "background-color: #ffe6e6;")
        phone_text = self.phone_input.text().strip()
        if phone_text:
            try:
                require_phone(phone_text)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.phone_input.setStyleSheet(self.phone_input.styleSheet() + "background-color: #ffe6e6;")
        email_text = self.email_input.text().strip()
        if email_text:
            try:
                require_email(email_text)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.email_input.setStyleSheet(self.email_input.styleSheet() + "background-color: #ffe6e6;")

        if errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(errors))
            return

        try:
            data = {
                'fullName': full_name,
                'phoneNumber': self.phone_input.text().strip() or None,
                'email': self.email_input.text().strip() or None,
                'isActive': self.active_checkbox.isChecked()
            }

            if self.client:
                self.api_service.update_client(self.client.id, **data)
                QMessageBox.information(self, "Успех", "✅ Клиент успешно обновлен!")
            else:
                self.api_service.create_client(
                    data['fullName'], data['phoneNumber'], data['email'])
                QMessageBox.information(self, "Успех", "✅ Клиент успешно добавлен!")

            self.accept()

        except Exception as e:
            dup = _check_duplicate(e, "ФИО", full_name)
            if dup:
                QMessageBox.warning(self, "Ошибка", dup)
            else:
                QMessageBox.warning(self, "Ошибка", f"❌ Ошибка: {e}")