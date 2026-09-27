"""
Виджет управления партиями товаров
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, 
    QLineEdit, QComboBox, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox, QDateEdit
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


class BatchesWidget(QWidget):
    """Виджет управления партиями"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, api_service: ApiService):
        super().__init__()
        
        self.api_service = api_service
        self.batches = []
        self.suppliers = []
        self.products = []
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
        
        title_label = QLabel("📦 Управление партиями")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.setMinimumWidth(80)
        self.add_btn.clicked.connect(self.add_batch)
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
        self.search_input.setPlaceholderText("Номер накладной...")
        self.search_input.setMinimumWidth(150)
        self.search_input.textChanged.connect(self.filter_batches)
        filter_layout.addWidget(self.search_input)
        
        supplier_label = QLabel("Поставщик:")
        filter_layout.addWidget(supplier_label)
        
        self.supplier_filter = QComboBox()
        self.supplier_filter.setMinimumWidth(150)
        self.supplier_filter.currentTextChanged.connect(self.filter_batches)
        filter_layout.addWidget(self.supplier_filter)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        self.batches_table = QTableWidget()
        self.batches_table.setColumnCount(7)
        self.batches_table.setHorizontalHeaderLabels([
            "ID", "Накладная", "Поставщик", "Дата поставки", "Кол-во", "Стоимость", "Действия"
        ])
        
        header = self.batches_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.batches_table.setAlternatingRowColors(True)
        self.batches_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.batches_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.batches_table.setMinimumHeight(300)
        
        main_layout.addWidget(self.batches_table)
        
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
            
            QLineEdit, QComboBox, QDateEdit {
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
        self.batches_table.doubleClicked.connect(self.edit_batch)
    
    def refresh_data(self):
        """Обновить данные"""
        try:
            if not self.api_service.token:
                self.logger.info("Пропуск обновления данных - пользователь не авторизован")
                return
            
            self.info_label.setText("Загрузка данных...")
            
            self.batches = self.api_service.get_batches()
            self.suppliers = self.api_service.get_suppliers()
            self.products = self.api_service.get_products()
            
            self.update_supplier_filter()
            self.filter_batches()
            
            self.info_label.setText("Данные загружены")
            self.logger.info(f"Загружено {len(self.batches)} партий")
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке партий: {e}")
            self.info_label.setText(f"Ошибка: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить партии: {e}")
    
    def update_supplier_filter(self):
        """Обновить фильтр поставщиков"""
        current_text = self.supplier_filter.currentText()
        
        self.supplier_filter.blockSignals(True)
        self.supplier_filter.clear()
        self.supplier_filter.addItem("Все поставщики")
        
        for supplier in sorted(self.suppliers, key=lambda x: x.get('name', '')):
            self.supplier_filter.addItem(supplier.get('name', ''), supplier.get('id'))
        
        index = self.supplier_filter.findText(current_text)
        if index >= 0:
            self.supplier_filter.setCurrentIndex(index)
        
        self.supplier_filter.blockSignals(False)
    
    def filter_batches(self):
        """Отфильтровать партии"""
        try:
            search_text = self.search_input.text().lower()
            supplier_text = self.supplier_filter.currentText()
            
            filtered = []
            for batch in self.batches:
                if search_text:
                    invoice = batch.get('invoiceNumber', '').lower()
                    if search_text not in invoice:
                        continue
                
                if supplier_text != "Все поставщики":
                    supplier_name = self.get_supplier_name(batch.get('supplierId'))
                    if supplier_name != supplier_text:
                        continue
                
                filtered.append(batch)
            
            self.update_table_with_batches(filtered)
            self.total_label.setText(f"Всего: {len(filtered)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при фильтрации: {e}")
    
    def get_supplier_name(self, supplier_id):
        """Получение названия поставщика"""
        if not supplier_id:
            return "Неизвестный"
        for supplier in self.suppliers:
            if supplier.get('id') == supplier_id:
                return supplier.get('name', 'Неизвестный')
        return "Неизвестный"
    
    def update_table_with_batches(self, batches):
        """Обновить таблицу с указанными партиями"""
        self.batches_table.setRowCount(len(batches))
        
        for row, batch in enumerate(batches):
            self.batches_table.setItem(row, 0, QTableWidgetItem(str(batch.get('id', 0))))
            self.batches_table.setItem(row, 1, QTableWidgetItem(batch.get('invoiceNumber', '-')))
            self.batches_table.setItem(row, 2, QTableWidgetItem(self.get_supplier_name(batch.get('supplierId'))))
            
            delivery_date = batch.get('deliveryDate', '')
            if delivery_date:
                try:
                    from datetime import datetime
                    if isinstance(delivery_date, str):
                        dt = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
                        delivery_date = dt.strftime("%d.%m.%Y")
                except:
                    pass
            self.batches_table.setItem(row, 3, QTableWidgetItem(str(delivery_date)))
            
            quantity = batch.get('quantity', 0) or 0
            qty_item = QTableWidgetItem(str(quantity))
            self.batches_table.setItem(row, 4, qty_item)
            
            try:
                cost = float(batch.get('costPrice') or 0)
            except (TypeError, ValueError):
                cost = 0.0
            cost_text = f"₽{cost:,.2f}"
            self.batches_table.setItem(row, 5, QTableWidgetItem(cost_text))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setFixedSize(28, 24)
            edit_btn.clicked.connect(lambda checked, b=batch: self.edit_batch_by_object(b))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Удалить")
            delete_btn.setFixedSize(28, 24)
            delete_btn.clicked.connect(lambda checked, b=batch: self.delete_batch_by_object(b))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.batches_table.setCellWidget(row, 6, actions_widget)
    
    def update_table(self):
        """Обновить таблицу"""
        self.filter_batches()
    
    def add_batch(self):
        """Добавить партию"""
        dialog = BatchDialog(self.api_service, self.suppliers, self, None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def edit_batch(self, index):
        """Редактировать партию"""
        row = index.row()
        _cell = self.batches_table.item(row, 0)
        try:
            batch_id = int(_cell.text()) if _cell is not None else -1
        except (TypeError, ValueError):
            batch_id = -1
        if batch_id < 0:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить ID записи")
            return
        batch = next((b for b in self.batches if b.get('id') == batch_id), None)
        if batch:
            self.edit_batch_by_object(batch)
    
    def edit_batch_by_object(self, batch):
        """Редактировать партию"""
        dialog = BatchDialog(self.api_service, self.suppliers, self, batch)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def delete_batch_by_object(self, batch):
        """Удалить партию"""
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить партию '{batch.get('invoiceNumber', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_service.delete_batch(batch.get('id'))
                QMessageBox.information(self, "Успех", "Партия успешно удалена")
                self.refresh_data()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить партию: {e}")


class BatchDialog(QDialog):
    """Диалог добавления/редактирования партии"""
    
    def __init__(self, api_service, suppliers, parent=None, batch=None):
        super().__init__(parent)
        
        self.api_service = api_service
        self.suppliers = suppliers
        self.batch = batch
        
        self.setup_ui()
        self.setup_styles()
        
        if batch:
            self.load_batch_data()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("➕ Добавление партии" if not self.batch else "✏️ Редактирование партии")
        self.setMinimumSize(450, 350)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        form_layout = QFormLayout()
        
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("Выберите поставщика", None)
        for supplier in self.suppliers:
            self.supplier_combo.addItem(supplier.get('name', ''), supplier.get('id'))
        form_layout.addRow("Поставщик *:", self.supplier_combo)
        
        self.invoice_input = QLineEdit()
        self.invoice_input.setPlaceholderText("Например: ПОСТ-001/2024")
        form_layout.addRow("Номер накладной *:", self.invoice_input)
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow("Дата поставки:", self.date_input)
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("0")
        form_layout.addRow("Количество:", self.quantity_input)
        
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("0.00")
        form_layout.addRow("Стоимость:", self.cost_input)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_batch)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def setup_styles(self):
        """Настройка стилей"""
        self.setStyleSheet("""
            QLineEdit, QComboBox, QDateEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)
    
    def load_batch_data(self):
        """Загрузить данные партии"""
        if self.batch:
            supplier_id = self.batch.get('supplierId')
            for i in range(self.supplier_combo.count()):
                if self.supplier_combo.itemData(i) == supplier_id:
                    self.supplier_combo.setCurrentIndex(i)
                    break
            
            self.invoice_input.setText(self.batch.get('invoiceNumber', ''))
            
            delivery_date = self.batch.get('deliveryDate', '')
            if delivery_date:
                try:
                    from datetime import datetime
                    if isinstance(delivery_date, str):
                        dt = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
                        self.date_input.setDate(QDate(dt.year, dt.month, dt.day))
                except:
                    pass
            
            self.quantity_input.setText(str(self.batch.get('quantity', 0)))
            self.cost_input.setText(str(self.batch.get('costPrice', 0)))
    
    def reset_field_styles(self):
        default = "padding: 5px; border: 1px solid #ddd; border-radius: 3px;"
        for inp in [self.invoice_input, self.quantity_input, self.cost_input]:
            inp.setStyleSheet(default)

    def save_batch(self):
        """Сохранить партию"""
        errors = []
        self.reset_field_styles()

        supplier_id = self.supplier_combo.currentData()
        if not supplier_id:
            errors.append("❌ Поле «Поставщик» обязательно для выбора.")

        invoice = self.invoice_input.text().strip()
        if not invoice:
            errors.append("❌ Поле «Номер накладной» обязательно для заполнения.")
            self.invoice_input.setStyleSheet(self.invoice_input.styleSheet() + "background-color: #ffe6e6;")
        else:
            try:
                from src.utils.validation import require_delivery_date, require_invoice_number
                require_invoice_number(invoice)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.invoice_input.setStyleSheet(self.invoice_input.styleSheet() + "background-color: #ffe6e6;")
            try:
                require_delivery_date(self.date_input.date().toPyDate())
            except Exception as e:
                errors.append(f"❌ {e}")

        quantity = 0
        qty_text = self.quantity_input.text().strip()
        if qty_text:
            err = _check_int(qty_text, "Количество", min_val=0)
            if err:
                errors.append(err)
                self.quantity_input.setStyleSheet(self.quantity_input.styleSheet() + "background-color: #ffe6e6;")
            else:
                quantity = int(qty_text)

        from src.utils.validation import require_positive_price
        cost = None
        cost_text = self.cost_input.text().strip()
        if cost_text:
            try:
                require_positive_price(cost_text, "Стоимость")
                cost = float(cost_text)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.cost_input.setStyleSheet(self.cost_input.styleSheet() + "background-color: #ffe6e6;")

        if errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(errors))
            return

        try:
            data = {
                'supplierId': supplier_id,
                'invoiceNumber': invoice,
                'deliveryDate': self.date_input.date().toPyDate(),
                'quantity': quantity,
                'costPrice': cost
            }

            if self.batch:
                self.api_service.update_batch(self.batch.get('id'), **data)
                QMessageBox.information(self, "Успех", "✅ Партия успешно обновлена!")
            else:
                self.api_service.create_batch(**data)
                QMessageBox.information(self, "Успех", "✅ Партия успешно добавлена!")

            self.accept()

        except Exception as e:
            dup = _check_duplicate(e, "номер накладной", invoice)
            if dup:
                QMessageBox.warning(self, "Ошибка", dup)
            else:
                QMessageBox.warning(self, "Ошибка", f"❌ Ошибка: {e}")