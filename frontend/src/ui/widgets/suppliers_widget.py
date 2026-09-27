"""
Виджет управления поставщиками
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, 
    QLineEdit, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.services.api_service import ApiService
from src.models import Supplier as SupplierModel


def _check_duplicate(exc, field_name, field_value):
    from src.utils.validation import format_duplicate_error
    return format_duplicate_error(exc, field_name, field_value)


class SuppliersWidget(QWidget):
    """Виджет управления поставщиками"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, api_service: ApiService):
        super().__init__()
        
        self.api_service = api_service
        self.suppliers = []
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.setup_styles()
        self.connect_signals()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🚚 Управление поставщиками")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.setMinimumWidth(80)
        self.add_btn.clicked.connect(self.add_supplier)
        header_layout.addWidget(self.add_btn)
        
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumWidth(80)
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        filter_layout = QHBoxLayout()
        
        search_label = QLabel("🔍 Поиск:")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Название поставщика...")
        self.search_input.setMinimumWidth(200)
        self.search_input.textChanged.connect(self.filter_suppliers)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(7)
        self.suppliers_table.setHorizontalHeaderLabels([
            "ID", "Название", "Телефон", "Email", "Адрес", "Реквизиты", "Действия"
        ])
        
        header = self.suppliers_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.suppliers_table.setAlternatingRowColors(True)
        self.suppliers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.suppliers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.suppliers_table.setMinimumHeight(300)
        
        main_layout.addWidget(self.suppliers_table)
        
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
        self.suppliers_table.doubleClicked.connect(self.edit_supplier)
    
    def refresh_data(self):
        """Обновить данные"""
        try:
            if not self.api_service.token:
                self.logger.info("Пропуск обновления данных - пользователь не авторизован")
                return
            
            self.info_label.setText("Загрузка данных...")
            
            suppliers_data = self.api_service.get_suppliers()
            self.suppliers = [SupplierModel.from_dict(s) for s in suppliers_data]
            
            self.filter_suppliers()
            
            self.info_label.setText("Данные загружены")
            self.logger.info(f"Загружено {len(self.suppliers)} поставщиков")
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке поставщиков: {e}")
            self.info_label.setText(f"Ошибка: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить поставщиков: {e}")
    
    def filter_suppliers(self):
        """Отфильтровать поставщиков"""
        try:
            search_text = self.search_input.text().lower()
            
            filtered = []
            for supplier in self.suppliers:
                if not search_text or search_text in supplier.name.lower():
                    filtered.append(supplier)
            
            self.update_table_with_suppliers(filtered)
            self.total_label.setText(f"Всего: {len(filtered)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при фильтрации: {e}")
    
    def update_table_with_suppliers(self, suppliers):
        """Обновить таблицу с указанными поставщиками"""
        self.suppliers_table.setRowCount(len(suppliers))
        
        for row, supplier in enumerate(suppliers):
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(str(supplier.id)))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier.name))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier.phone_number or "-"))
            self.suppliers_table.setItem(row, 3, QTableWidgetItem(supplier.email or "-"))
            self.suppliers_table.setItem(row, 4, QTableWidgetItem(supplier.address or "-"))
            self.suppliers_table.setItem(row, 5, QTableWidgetItem(supplier.details or "-"))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setFixedSize(28, 24)
            edit_btn.clicked.connect(lambda checked, s=supplier: self.edit_supplier_by_object(s))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Удалить")
            delete_btn.setFixedSize(28, 24)
            delete_btn.clicked.connect(lambda checked, s=supplier: self.delete_supplier_by_object(s))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.suppliers_table.setCellWidget(row, 6, actions_widget)
    
    def update_table(self):
        """Обновить таблицу"""
        self.filter_suppliers()
    
    def add_supplier(self):
        """Добавить поставщика"""
        dialog = SupplierDialog(self.api_service, self, None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def edit_supplier(self, index):
        """Редактировать поставщика"""
        row = index.row()
        _cell = self.suppliers_table.item(row, 0)
        try:
            supplier_id = int(_cell.text()) if _cell is not None else -1
        except (TypeError, ValueError):
            supplier_id = -1
        if supplier_id < 0:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить ID записи")
            return
        self.edit_supplier_by_id(supplier_id)
    
    def edit_supplier_by_id(self, supplier_id):
        """Редактировать поставщика по ID"""
        try:
            supplier = next((s for s in self.suppliers if s.id == supplier_id), None)
            if supplier:
                self.edit_supplier_by_object(supplier)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить поставщика: {e}")
    
    def edit_supplier_by_object(self, supplier):
        """Редактировать поставщика"""
        dialog = SupplierDialog(self.api_service, self, supplier)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def delete_supplier_by_object(self, supplier):
        """Удалить поставщика"""
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить поставщика '{supplier.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_service.delete_supplier(supplier.id)
                QMessageBox.information(self, "Успех", "Поставщик успешно удален")
                self.refresh_data()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить поставщика: {e}")


class SupplierDialog(QDialog):
    """Диалог добавления/редактирования поставщика"""
    
    def __init__(self, api_service, parent=None, supplier: SupplierModel = None):
        super().__init__(parent)
        
        self.api_service = api_service
        self.supplier = supplier
        
        self.setup_ui()
        self.setup_styles()
        
        if supplier:
            self.load_supplier_data()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("➕ Добавление поставщика" if not self.supplier else "✏️ Редактирование поставщика")
        self.setMinimumSize(450, 350)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: ООО Цветы России")
        form_layout.addRow("Название *:", self.name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+74951234567")
        form_layout.addRow("Телефон:", self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Город, улица, дом")
        form_layout.addRow("Адрес:", self.address_input)
        
        self.details_input = QLineEdit()
        self.details_input.setPlaceholderText("ИНН, ОГРН и т.д.")
        form_layout.addRow("Реквизиты:", self.details_input)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_supplier)
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
    
    def load_supplier_data(self):
        """Загрузить данные поставщика"""
        if self.supplier:
            self.name_input.setText(self.supplier.name)
            self.phone_input.setText(self.supplier.phone_number or "")
            self.email_input.setText(self.supplier.email or "")
            self.address_input.setText(self.supplier.address or "")
            self.details_input.setText(self.supplier.details or "")
    
    def reset_field_styles(self):
        default = "padding: 5px; border: 1px solid #ddd; border-radius: 3px;"
        for inp in [self.name_input, self.phone_input, self.email_input, self.address_input, self.details_input]:
            inp.setStyleSheet(default)

    def save_supplier(self):
        """Сохранить поставщика"""
        errors = []
        self.reset_field_styles()

        name = self.name_input.text().strip()
        if not name:
            errors.append("❌ Поле «Название» обязательно для заполнения.")
            self.name_input.setStyleSheet(self.name_input.styleSheet() + "background-color: #ffe6e6;")

        from src.utils.validation import require_email, require_name, require_phone
        if name:
            try:
                require_name(name, "Название поставщика")
            except Exception as e:
                errors.append(f"❌ {e}")
                self.name_input.setStyleSheet(self.name_input.styleSheet() + "background-color: #ffe6e6;")
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
                'name': name,
                'phoneNumber': self.phone_input.text().strip() or None,
                'email': self.email_input.text().strip() or None,
                'address': self.address_input.text().strip() or None,
                'details': self.details_input.text().strip() or None
            }

            if self.supplier:
                self.api_service.update_supplier(self.supplier.id, **data)
                QMessageBox.information(self, "Успех", "✅ Поставщик успешно обновлен!")
            else:
                self.api_service.create_supplier(**data)
                QMessageBox.information(self, "Успех", "✅ Поставщик успешно добавлен!")

            self.accept()

        except Exception as e:
            dup = _check_duplicate(e, "название", name)
            if dup:
                QMessageBox.warning(self, "Ошибка", dup)
            else:
                QMessageBox.warning(self, "Ошибка", f"❌ Ошибка: {e}")