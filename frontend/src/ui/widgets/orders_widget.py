"""
Виджет управления заказами
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
from src.models import Order, Client, Employee


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


class OrdersWidget(QWidget):
    """Виджет управления заказами"""
    
    # Сигнал обновления данных
    data_updated = pyqtSignal()
    
    def __init__(self, api_service: ApiService):
        super().__init__()
        
        self.api_service = api_service
        self.orders = []
        self.clients = []
        self.employees = []
        
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
        title_label = QLabel("🛒 Управление заказами")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Адаптивные кнопки действий
        self.add_order_btn = QPushButton("➕ Создать")
        self.add_order_btn.setMinimumWidth(80)
        self.add_order_btn.clicked.connect(self.add_order)
        header_layout.addWidget(self.add_order_btn)
        
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumWidth(80)
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Адаптивная панель поиска и фильтров
        filter_layout = QHBoxLayout()
        
        # Поиск с иконкой
        search_label = QLabel("🔍 Поиск:")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите номер заказа или имя клиента...")
        self.search_input.setMinimumWidth(200)
        self.search_input.textChanged.connect(self.filter_orders)
        filter_layout.addWidget(self.search_input)
        
        # Фильтр по статусу с иконкой
        status_label = QLabel("📊 Статус:")
        filter_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.setMinimumWidth(120)
        self.status_filter.addItems(["Все", "Новый", "В обработке", "Готов к выдаче", "Выполнен", "Отменен"])
        self.status_filter.currentTextChanged.connect(self.filter_orders)
        filter_layout.addWidget(self.status_filter)
        
# Фильтр по дате с иконкой
        date_label = QLabel("📅 Дата:")
        filter_layout.addWidget(date_label)
        
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        
        # Кнопка сброса фильтра даты
        self.reset_date_btn = QPushButton("×")
        self.reset_date_btn.setToolTip("Показать все даты")
        self.reset_date_btn.setFixedSize(25, 25)
        self.reset_date_btn.clicked.connect(self.reset_date_filter)
        self.reset_date_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #666;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ccc;
            }
        """)
        filter_layout.addWidget(self.reset_date_btn)
        
        self.use_date_filter = False  # Флаг использования фильтра по дате
        self.date_filter.dateChanged.connect(self.on_date_changed)
        
        filter_layout.addStretch()  # Растягиваем для адаптивности
        main_layout.addLayout(filter_layout)
        
        # Таблица заказов
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "ID", "Номер", "Дата", "Клиент", "Сумма", "Статус", "Действия"
        ])
        
        # Настройка таблицы
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Клиент растягивается
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Номер
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Дата
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Сумма
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Статус
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Действия
        
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.orders_table)
        
        # Информационная панель
        info_layout = QHBoxLayout()
        
        self.info_label = QLabel("Загрузка данных...")
        info_layout.addWidget(self.info_label)
        
        info_layout.addStretch()
        
        self.total_label = QLabel("Всего: 0")
        info_layout.addWidget(self.total_label)
        
        self.revenue_label = QLabel("Выручка: ₽0")
        info_layout.addWidget(self.revenue_label)
        
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
            
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            
            QDateEdit {
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
            
            QPushButton#reset_date {
                background-color: #e0e0e0;
                color: #666;
                border-radius: 12px;
                font-weight: bold;
            }
        """)
    
    def connect_signals(self):
        """Подключение сигналов"""
        self.data_updated.connect(self.update_table)
        self.orders_table.doubleClicked.connect(self.edit_order)
    
    def refresh_data(self):
        """Обновить данные"""
        try:
            # Проверяем, есть ли токен авторизации
            if not self.api_service.token:
                self.logger.info("Пропуск обновления данных - пользователь не авторизован")
                return
            
            self.info_label.setText("Загрузка данных...")
            
            # Загружаем заказы, клиентов и сотрудников
            orders_data = self.api_service.get_orders()
            self.logger.info(f"Получено {len(orders_data)} заказов из API")
            
            # Логируем структуру данных для отладки
            if orders_data:
                first_order = orders_data[0]
                self.logger.info(f"Структура первого заказа: {list(first_order.keys())}")
                if 'client' in first_order:
                    self.logger.info(f"Структура клиента: {list(first_order['client'].keys())}")
                else:
                    self.logger.warning("В заказе отсутствует поле 'client'")
            
            self.orders = [Order.from_dict(o) for o in orders_data]
            self.clients = [Client.from_dict(c) for c in self.api_service.get_clients()]
            self.employees = [Employee.from_dict(e) for e in self.api_service.get_employees()]  # Исправлено
            
            # Применяем фильтры
            self.filter_orders()
            
            self.info_label.setText("Данные загружены")
            self.logger.info(f"Загружено {len(self.orders)} заказов")
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке заказов: {e}")
            self.info_label.setText(f"Ошибка: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить заказы: {e}")
    
    def filter_orders(self):
        """Отфильтровать заказы"""
        try:
            search_text = self.search_input.text().lower()
            status_filter = self.status_filter.currentText()
            
            filtered_orders = []
            total_revenue = 0
            
            for order in self.orders:
                # Фильтр по поиску
                if search_text and not (
                    search_text in order.order_number.lower() or
                    search_text in order.client_name.lower()
                ):
                    continue
                
                # Фильтр по статусу
                if status_filter != "Все" and order.status != status_filter:
                    continue
                
                # Фильтр по дате (только если включен)
                if self.use_date_filter:
                    date_filter = self.date_filter.date().toPyDate()
                    if order.order_date != date_filter:
                        continue
                
                filtered_orders.append(order)
                total_revenue += float(order.total_amount)
            
            # Обновляем таблицу
            self.update_table_with_orders(filtered_orders)
            
            # Обновляем счетчики
            self.total_label.setText(f"Всего: {len(filtered_orders)}")
            self.revenue_label.setText(f"Выручка: ₽{total_revenue:,.2f}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при фильтрации заказов: {e}")
    
    def on_date_changed(self, date):
        """Обработка изменения даты"""
        self.use_date_filter = True
        self.filter_orders()
    
    def reset_date_filter(self):
        """Сброс фильтра по дате"""
        self.use_date_filter = False
        self.filter_orders()
    
    def update_table_with_orders(self, orders):
        """Обновить таблицу с указанными заказами"""
        self.orders_table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            # ID
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order.id)))
            
            # Номер
            self.orders_table.setItem(row, 1, QTableWidgetItem(order.order_number))
            
            # Дата
            date_text = order.order_date.strftime("%d.%m.%Y")
            self.orders_table.setItem(row, 2, QTableWidgetItem(date_text))
            
            # Клиент
            self.orders_table.setItem(row, 3, QTableWidgetItem(order.client_name))
            
            # Сумма
            amount_text = f"₽{order.total_amount:,.2f}"
            self.orders_table.setItem(row, 4, QTableWidgetItem(amount_text))
            
            # Статус
            status_item = QTableWidgetItem(order.status)
            self.orders_table.setItem(row, 5, status_item)
            
            # Цвет статуса (устанавливаем через таблицу)
            status_colors = {
                'Новый': '#2196F3',
                'В обработке': '#FF9800',
                'Готов к выдаче': '#4CAF50',
                'Выполнен': '#9C27B0',
                'Отменен': '#F44336'
            }
            color = status_colors.get(order.status, '#757575')
            status_item.setForeground(QBrush(QColor(color)))
            font = status_item.font()
            font.setBold(True)
            status_item.setFont(font)
            
            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setFixedSize(28, 24)
            edit_btn.clicked.connect(lambda checked, o=order: self.edit_order_by_object(o))
            
            cancel_btn = QPushButton("🗑️")
            cancel_btn.setToolTip("Отменить")
            cancel_btn.setFixedSize(28, 24)
            cancel_btn.clicked.connect(lambda checked, o=order: self.cancel_order_by_object(o))
            cancel_btn.setEnabled(order.can_cancel)
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(cancel_btn)
            
            self.orders_table.setCellWidget(row, 6, actions_widget)
    
    def update_table(self):
        """Обновить таблицу"""
        self.filter_orders()
    
    def add_order(self):
        """Создать заказ"""
        dialog = OrderDialog(self.api_service, self.clients, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def edit_order(self, index):
        """Редактировать заказ по индексу таблицы"""
        row = index.row()
        item = self.orders_table.item(row, 0)
        if item is None:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить ID заказа")
            return
        order_id = int(item.text())
        self.edit_order_by_id(order_id)
    
    def edit_order_by_id(self, order_id):
        """Редактировать заказ по ID"""
        try:
            order_data = self.api_service.get_order(order_id)
            order = Order.from_dict(order_data)
            self.edit_order_by_object(order)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить заказ: {e}")
    
    def edit_order_by_object(self, order):
        """Редактировать заказ"""
        dialog = OrderDialog(self.api_service, self.clients, self, order)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def cancel_order_by_object(self, order):
        """Отменить заказ"""
        if not order.can_cancel:
            QMessageBox.warning(self, "Ошибка", "Этот заказ нельзя отменить")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение отмены",
            f"Вы уверены, что хотите отменить заказ '{order.order_number}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_service.delete_order(order.id)
                QMessageBox.information(self, "Успех", "Заказ успешно отменен")
                self.refresh_data()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось отменить заказ: {e}")


class OrderDialog(QDialog):
    """Диалог создания/редактирования заказа"""
    
    def __init__(self, api_service: ApiService, clients: list, parent=None, order: Order = None):
        super().__init__(parent)
        
        self.api_service = api_service
        self.clients = clients
        self.order = order
        
        self.setup_ui()
        self.setup_styles()
        
        if order:
            self.load_order_data()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Создание заказа" if not self.order else "Редактирование заказа")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        # Клиент
        self.client_combo = QComboBox()
        self.client_combo.addItem("Выберите клиента")
        for client in self.clients:
            self.client_combo.addItem(client.full_name, client.id)
        form_layout.addRow("Клиент *:", self.client_combo)
        
        # Номер заказа
        self.order_number_input = QLineEdit()
        self.order_number_input.setPlaceholderText("Автоматически")
        form_layout.addRow("Номер заказа:", self.order_number_input)
        
        # Дата заказа
        self.order_date_input = QDateEdit()
        self.order_date_input.setDate(QDate.currentDate())
        self.order_date_input.setCalendarPopup(True)
        form_layout.addRow("Дата заказа:", self.order_date_input)
        
        # Статус (только допустимые: Новый, В обработке, Выполнен, Доставлен)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "В обработке", "Выполнен", "Доставлен"])
        form_layout.addRow("Статус:", self.status_combo)
        
        # Общая сумма
        self.total_amount_input = QLineEdit("0.00")
        self.total_amount_input.setEnabled(False)
        form_layout.addRow("Общая сумма:", self.total_amount_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_order)
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
            
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            
            QDateEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)
    
    def load_order_data(self):
        """Загрузить данные заказа"""
        if self.order:
            # Выбор клиента
            if self.order.client_id:
                for i in range(self.client_combo.count()):
                    if self.client_combo.itemData(i) == self.order.client_id:
                        self.client_combo.setCurrentIndex(i)
                        break
            
            self.order_number_input.setText(self.order.order_number)
            self.order_date_input.setDate(QDate(self.order.order_date.year, self.order.order_date.month, self.order.order_date.day))
            self.status_combo.setCurrentText(self.order.status)
            self.total_amount_input.setText(str(self.order.total_amount))
    
    def save_order(self):
        """Сохранить заказ"""
        errors = []

        if self.client_combo.currentData() is None:
            errors.append("❌ Поле «Клиент» обязательно для выбора.")
            self.client_combo.setStyleSheet(self.client_combo.styleSheet() + "background-color: #ffe6e6;")

        from src.utils.validation import require_order_date, require_order_number, require_order_status
        order_number_text = self.order_number_input.text().strip()
        if order_number_text:
            try:
                require_order_number(order_number_text)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.order_number_input.setStyleSheet(self.order_number_input.styleSheet() + "background-color: #ffe6e6;")
        try:
            require_order_status(self.status_combo.currentText())
        except Exception as e:
            errors.append(f"❌ {e}")
        try:
            require_order_date(self.order_date_input.date().toPyDate())
        except Exception as e:
            errors.append(f"❌ {e}")

        total_text = self.total_amount_input.text().strip()
        if total_text:
            err = _check_decimal(total_text, "Общая сумма", min_val=0)
            if err:
                errors.append(err)
                self.total_amount_input.setStyleSheet(self.total_amount_input.styleSheet() + "background-color: #ffe6e6;")

        if errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(errors))
            return

        try:
            data = {
                'clientId': self.client_combo.currentData(),
                'orderNumber': self.order_number_input.text().strip() or None,
                'orderDate': self.order_date_input.date().toPyDate(),
                'status': self.status_combo.currentText(),
                'totalAmount': float(total_text or 0)
            }

            if self.order:
                self.api_service.update_order(self.order.id, **data)
                QMessageBox.information(self, "Успех", "✅ Заказ успешно обновлен!")
            else:
                self.api_service.create_order(**data)
                QMessageBox.information(self, "Успех", "✅ Заказ успешно создан!")

            self.accept()

        except Exception as e:
            dup = _check_duplicate(e, "номер заказа", data.get('orderNumber', ''))
            if dup:
                QMessageBox.warning(self, "Ошибка", dup)
            else:
                QMessageBox.warning(self, "Ошибка", f"❌ Ошибка: {e}")