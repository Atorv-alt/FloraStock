"""
Виджет управления складом
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, 
    QLineEdit, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QBrush, QColor

from src.services.api_service import ApiService


def _check_int(value, field_name, max_val=2147483647, min_val=None):
    try:
        v = int(value)
        if v > max_val:
            return f"❌ Поле «{field_name}» превышает максимальное значение ({max_val:,})."
        if min_val is not None and v < min_val:
            if min_val == 0:
                return f"❌ Поле «{field_name}» не может быть отрицательным."
            return f"❌ Поле «{field_name}» должно быть не меньше {min_val}."
        return None
    except (ValueError, TypeError):
        return f"❌ Поле «{field_name}» должно быть целым числом."


def _check_decimal(value, field_name, max_val=999999999.99, min_val=None):
    try:
        v = float(value)
        if v > max_val:
            return f"❌ Поле «{field_name}» превышает максимальное значение ({max_val:,.2f})."
        if min_val is not None and v < min_val:
            if min_val == 0:
                return f"❌ Поле «{field_name}» не может быть отрицательным."
            return f"❌ Поле «{field_name}» должно быть не меньше {min_val}."
        return None
    except (ValueError, TypeError):
        return f"❌ Поле «{field_name}» должно быть числом."


def _check_duplicate(exc, field_name, field_value):
    from src.utils.validation import format_duplicate_error
    return format_duplicate_error(exc, field_name, field_value)


class InventoryWidget(QWidget):
    """Виджет управления складом"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, api_service: ApiService):
        super().__init__()
        
        self.api_service = api_service
        self.inventory = []
        self.products = []
        self.batches = []
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
        
        title_label = QLabel("📋 Управление складом")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.setMinimumWidth(80)
        self.add_btn.clicked.connect(self.add_inventory)
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
        self.search_input.setPlaceholderText("Введите название товара...")
        self.search_input.setMinimumWidth(150)
        self.search_input.textChanged.connect(self.filter_inventory)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Товар", "Партия", "Количество", "Место хранения", "Температура"
        ])
        
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.inventory_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.inventory_table.setMinimumHeight(300)
        
        main_layout.addWidget(self.inventory_table)
        
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
        self.inventory_table.doubleClicked.connect(self.edit_inventory)
    
    def refresh_data(self):
        """Обновить данные"""
        try:
            if not self.api_service.token:
                self.logger.info("Пропуск обновления данных - пользователь не авторизован")
                return
            
            self.info_label.setText("Загрузка данных...")
            
            self.inventory = self.api_service.get_inventory()
            self.products = self.api_service.get_products()
            self.batches = self.api_service.get_batches()
            
            self.filter_inventory()
            
            self.info_label.setText("Данные загружены")
            self.logger.info(f"Загружено {len(self.inventory)} записей склада")
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке склада: {e}")
            self.info_label.setText(f"Ошибка: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные склада: {e}")
    
    def filter_inventory(self):
        """Отфильтровать записи"""
        try:
            search_text = self.search_input.text().lower()
            
            filtered = []
            for item in self.inventory:
                product_name = self.get_product_name(item.get('productId'))
                if search_text and search_text not in product_name.lower():
                    continue
                filtered.append(item)
            
            self.update_table_with_inventory(filtered)
            self.total_label.setText(f"Всего: {len(filtered)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при фильтрации: {e}")
    
    def update_table_with_inventory(self, items):
        """Обновить таблицу с указанными записями"""
        self.inventory_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(item.get('id', 0))))
            
            product_name = self.get_product_name(item.get('productId'))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(product_name))
            
            batch_info = self.get_batch_info(item.get('batchId'))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(batch_info))
            
            quantity = item.get('quantity', 0)
            qty_item = QTableWidgetItem(str(quantity))
            if quantity <= 10:
                qty_item.setForeground(QBrush(QColor("#f44336")))
            elif quantity <= 20:
                qty_item.setForeground(QBrush(QColor("#ff9800")))
            self.inventory_table.setItem(row, 3, qty_item)
            
            location = item.get('storageLocation', '-')
            self.inventory_table.setItem(row, 4, QTableWidgetItem(location or '-'))
            
            temp = item.get('storageTemperature', '-')
            self.inventory_table.setItem(row, 5, QTableWidgetItem(temp or '-'))
    
    def update_table(self):
        """Обновить таблицу"""
        self.filter_inventory()
    
    def get_product_name(self, product_id):
        """Получение названия товара по ID"""
        if not product_id:
            return "Неизвестный товар"
        for product in self.products:
            if product.get('id') == product_id:
                return product.get('name', 'Неизвестный товар')
        return "Неизвестный товар"
    
    def get_batch_info(self, batch_id):
        """Получение информации о партии"""
        if not batch_id:
            return "-"
        for batch in self.batches:
            if batch.get('id') == batch_id:
                invoice = batch.get('invoiceNumber', '')
                return f"#{batch_id}" + (f" ({invoice})" if invoice else "")
        return f"#{batch_id}"
    
    def add_inventory(self):
        """Добавить запись"""
        dialog = InventoryDialog(self.api_service, self.products, self.batches, self, None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def edit_inventory(self, index):
        """Редактировать запись"""
        row = index.row()
        item_id = int(self.inventory_table.item(row, 0).text())
        item = next((i for i in self.inventory if i.get('id') == item_id), None)
        if item:
            dialog = InventoryDialog(self.api_service, self.products, self.batches, self, item)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_data()
    
    def delete_inventory(self, item):
        """Удалить запись"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить запись о товаре '{self.get_product_name(item.get('productId'))}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_service.delete_inventory(item.get('id'))
                QMessageBox.information(self, "Успех", "Запись удалена")
                self.refresh_data()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить запись: {e}")


class InventoryDialog(QDialog):
    """Диалог добавления/редактирования записи склада"""
    
    def __init__(self, api_service, products, batches, parent=None, inventory_item=None):
        super().__init__(parent)
        
        self.api_service = api_service
        self.products = products
        self.batches = batches
        self.inventory_item = inventory_item
        
        self.setup_ui()
        self.setup_styles()
        
        if inventory_item:
            self.load_data()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Добавление записи" if not self.inventory_item else "Редактирование записи")
        self.setMinimumSize(450, 300)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        form_layout = QFormLayout()
        
        self.product_combo = QComboBox()
        self.product_combo.addItem("Выберите товар", None)
        for product in self.products:
            self.product_combo.addItem(product.get('name', 'Unknown'), product.get('id'))
        form_layout.addRow("Товар *:", self.product_combo)
        
        self.batch_combo = QComboBox()
        self.batch_combo.addItem("Выберите партию", None)
        for batch in self.batches:
            invoice = batch.get('invoiceNumber', '')
            text = f"#{batch.get('id')}" + (f" ({invoice})" if invoice else "")
            self.batch_combo.addItem(text, batch.get('id'))
        form_layout.addRow("Партия:", self.batch_combo)
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("0")
        form_layout.addRow("Количество:", self.quantity_input)
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Например: Холодильник А1")
        form_layout.addRow("Место хранения:", self.location_input)
        
        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("Например: +2°C")
        form_layout.addRow("Температура:", self.temp_input)
        
        self.humidity_input = QLineEdit()
        self.humidity_input.setPlaceholderText("Например: 85%")
        form_layout.addRow("Влажность:", self.humidity_input)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def setup_styles(self):
        """Настройка стилей"""
        self.setStyleSheet("""
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)
    
    def load_data(self):
        """Загрузить данные"""
        if self.inventory_item:
            product_id = self.inventory_item.get('productId')
            for i in range(self.product_combo.count()):
                if self.product_combo.itemData(i) == product_id:
                    self.product_combo.setCurrentIndex(i)
                    break
            
            batch_id = self.inventory_item.get('batchId')
            for i in range(self.batch_combo.count()):
                if self.batch_combo.itemData(i) == batch_id:
                    self.batch_combo.setCurrentIndex(i)
                    break
            
            self.quantity_input.setText(str(self.inventory_item.get('quantity', 0)))
            self.location_input.setText(self.inventory_item.get('storageLocation', '') or '')
            self.temp_input.setText(self.inventory_item.get('storageTemperature', '') or '')
            self.humidity_input.setText(self.inventory_item.get('humidityLevel', '') or '')
    
    def reset_field_styles(self):
        default = "padding: 5px; border: 1px solid #ddd; border-radius: 3px;"
        for inp in [self.quantity_input, self.location_input, self.temp_input, self.humidity_input]:
            inp.setStyleSheet(default)

    def save(self):
        """Сохранить запись"""
        errors = []
        self.reset_field_styles()

        product_id = self.product_combo.currentData()
        if not product_id:
            errors.append("❌ Поле «Товар» обязательно для выбора.")

        quantity = 0
        qty_text = self.quantity_input.text().strip()
        if qty_text:
            try:
                from src.utils.validation import require_non_negative_int
                quantity = require_non_negative_int(qty_text, "Количество на складе")
                if quantity > 2147483647:
                    raise ValueError("превышено максимальное значение")
            except Exception as e:
                errors.append(f"❌ {e}")
                self.quantity_input.setStyleSheet(self.quantity_input.styleSheet() + "background-color: #ffe6e6;")

        if errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(errors))
            return

        try:
            data = {
                'productId': product_id,
                'batchId': self.batch_combo.currentData(),
                'quantity': quantity,
                'storageLocation': self.location_input.text().strip() or None,
                'storageTemperature': self.temp_input.text().strip() or None,
                'humidityLevel': self.humidity_input.text().strip() or None
            }

            if self.inventory_item:
                self.api_service.update_inventory(self.inventory_item.get('id'), **data)
                QMessageBox.information(self, "Успех", "✅ Запись успешно обновлена!")
            else:
                self.api_service.create_inventory(**data)
                QMessageBox.information(self, "Успех", "✅ Запись успешно добавлена!")

            self.accept()

        except Exception as e:
            dup = _check_duplicate(e, "товар", str(product_id))
            if dup:
                QMessageBox.warning(self, "Ошибка", dup)
            else:
                QMessageBox.warning(self, "Ошибка", f"❌ Ошибка: {e}")