"""
Виджет управления товарами
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, 
    QLineEdit, QComboBox, QCheckBox, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.services.api_service import ApiService
from src.models import Product, Category


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


class ProductsWidget(QWidget):
    """Виджет управления товарами"""
    
    # Сигнал обновления данных
    data_updated = pyqtSignal()
    
    def __init__(self, api_service: ApiService):
        super().__init__()
        
        self.api_service = api_service
        self.products = []
        self.categories = []
        
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
        
        # Адаптивная панель инструментов
        header_layout = QHBoxLayout()
        
        # Заголовок с иконкой и адаптивным размером
        title_label = QLabel("🌺 Управление товарами")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Адаптивные кнопки действий с минимальными размерами
        self.add_product_btn = QPushButton("➕ Добавить")
        self.add_product_btn.setMinimumWidth(80)
        self.add_product_btn.clicked.connect(self.add_product)
        header_layout.addWidget(self.add_product_btn)
        
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
        self.search_input.setPlaceholderText("Введите название товара...")
        self.search_input.setMinimumWidth(150)
        self.search_input.textChanged.connect(self.filter_products)
        filter_layout.addWidget(self.search_input)
        
        # Фильтр по категории с иконкой
        category_label = QLabel("📂 Категория:")
        filter_layout.addWidget(category_label)
        
        self.category_filter = QComboBox()
        self.category_filter.setMinimumWidth(120)
        self.category_filter.addItem("Все категории")
        self.category_filter.currentTextChanged.connect(self.filter_products)
        filter_layout.addWidget(self.category_filter)
        
        filter_layout.addStretch()  # Растягиваем для адаптивности
        
        # Фильтр по статусу
        status_label = QLabel("Статус:")
        filter_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "Активные", "Неактивные"])
        self.status_filter.currentTextChanged.connect(self.filter_products)
        filter_layout.addWidget(self.status_filter)
        
        main_layout.addLayout(filter_layout)
        
        # Адаптивная таблица товаров
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Название", "Категория", "Цена", "Кол-во", "Статус", "Действия"
        ])
        
        # Адаптивная настройка таблицы
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Название растягивается
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Категория
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Цена
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Количество
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Статус
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Действия - фиксированная ширина
        header.resizeSection(6, 100)  # Фиксированная ширина для кнопок
        
        # Адаптивные стили таблицы
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setSortingEnabled(True)
        self.products_table.setMinimumHeight(300)  # Минимальная высота для адаптивности
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Категория
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Цена
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Кол-во
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Статус
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Действия
        
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.products_table)
        
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
            
            QComboBox {
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
        self.products_table.doubleClicked.connect(self.edit_product)
    
    def refresh_data(self):
        """Обновить данные"""
        try:
            # Проверяем, есть ли токен авторизации
            if not self.api_service.token:
                self.logger.info("Пропуск обновления данных - пользователь не авторизован")
                return
            
            self.info_label.setText("Загрузка данных...")
            
            # Загружаем товары и категории
            self.products = [Product.from_dict(p) for p in self.api_service.get_products()]
            self.categories = [Category.from_dict(c) for c in self.api_service.get_categories()]
            
            # Обновляем фильтр категорий
            self.update_category_filter()
            
            # Применяем фильтры
            self.filter_products()
            
            self.info_label.setText("Данные загружены")
            self.logger.info(f"Загружено {len(self.products)} товаров")
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке товаров: {e}")
            self.info_label.setText(f"Ошибка: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить товары: {e}")
    
    def update_category_filter(self):
        """Обновить фильтр категорий"""
        # Сохраняем текущий выбор
        current_text = self.category_filter.currentText()
        
        # Блокируем сигналы
        self.category_filter.blockSignals(True)
        
        # Очищаем и заполняем заново
        self.category_filter.clear()
        self.category_filter.addItem("Все категории")
        
        for category in sorted(self.categories, key=lambda x: x.name):
            self.category_filter.addItem(category.name)
        
        # Восстанавливаем выбор
        index = self.category_filter.findText(current_text)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
        
        # Включаем сигналы
        self.category_filter.blockSignals(False)
    
    def filter_products(self):
        """Отфильтровать товары"""
        try:
            search_text = self.search_input.text().lower()
            category_filter = self.category_filter.currentText()
            status_filter = self.status_filter.currentText()
            
            filtered_products = []
            
            for product in self.products:
                # Фильтр по поиску
                if search_text and search_text not in product.name.lower():
                    continue
                
                # Фильтр по категории
                if category_filter != "Все категории":
                    if not product.category or product.category.name != category_filter:
                        continue
                
                # Фильтр по статусу
                if status_filter == "Активные" and not product.is_active:
                    continue
                elif status_filter == "Неактивные" and product.is_active:
                    continue
                
                filtered_products.append(product)
            
            # Обновляем таблицу
            self.update_table_with_products(filtered_products)
            
            # Обновляем счетчик
            self.total_label.setText(f"Всего: {len(filtered_products)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при фильтрации товаров: {e}")
    
    def update_table_with_products(self, products):
        """Обновить таблицу с указанными товарами"""
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # ID
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product.id)))
            
            # Название
            self.products_table.setItem(row, 1, QTableWidgetItem(product.name))
            
            # Категория
            category_name = product.category_name
            self.products_table.setItem(row, 2, QTableWidgetItem(category_name))
            
            # Цена
            price_text = f"₽{product.retail_price:.2f}"
            self.products_table.setItem(row, 3, QTableWidgetItem(price_text))
            
            # Количество (заглушка, будет получено из API)
            self.products_table.setItem(row, 4, QTableWidgetItem("-"))
            
            # Статус
            status_text = "Активен" if product.is_active else "Неактивен"
            status_item = QTableWidgetItem(status_text)
            if product.is_active:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.products_table.setItem(row, 5, status_item)
            
            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setFixedSize(28, 24)
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product_by_object(p))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Удалить")
            delete_btn.setFixedSize(28, 24)
            delete_btn.clicked.connect(lambda checked, p=product: self.delete_product_by_object(p))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.products_table.setCellWidget(row, 6, actions_widget)
    
    def update_table(self):
        """Обновить таблицу"""
        self.filter_products()
    
    def add_product(self):
        """Добавить товар"""
        dialog = ProductDialog(self.api_service, self.categories, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def edit_product(self, index):
        """Редактировать товар по индексу таблицы"""
        row = index.row()
        _cell = self.products_table.item(row, 0)
        try:
            product_id = int(_cell.text()) if _cell is not None else -1
        except (TypeError, ValueError):
            product_id = -1
        if product_id < 0:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить ID записи")
            return
        self.edit_product_by_id(product_id)
    
    def edit_product_by_id(self, product_id):
        """Редактировать товар по ID"""
        try:
            product_data = self.api_service.get_product(product_id)
            product = Product.from_dict(product_data)
            self.edit_product_by_object(product)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить товар: {e}")
    
    def edit_product_by_object(self, product):
        """Редактировать товар"""
        dialog = ProductDialog(self.api_service, self.categories, self, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def delete_product_by_object(self, product):
        """Удалить товар"""
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить товар '{product.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_service.delete_product(product.id)
                QMessageBox.information(self, "Успех", "Товар успешно удален")
                self.refresh_data()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить товар: {e}")


class ProductDialog(QDialog):
    """Диалог добавления/редактирования товара"""
    
    def __init__(self, api_service: ApiService, categories: list, parent=None, product: Product = None):
        super().__init__(parent)
        
        self.api_service = api_service
        self.categories = categories
        self.product = product
        
        self.setup_ui()
        self.setup_styles()
        
        if product:
            self.load_product_data()
    
    def setup_ui(self):
        """Настройка адаптивного пользовательского интерфейса"""
        self.setWindowTitle("📦 Добавление товара" if not self.product else "✏️ Редактирование товара")
        self.setMinimumSize(400, 300)  # Минимальный размер для адаптивности
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Адаптивная форма
        form_layout = QFormLayout()
        
        # Название с адаптивными настройками
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название товара")
        self.name_input.setMinimumWidth(250)
        form_layout.addRow("Название *:", self.name_input)
        
        # Описание
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Введите описание товара")
        form_layout.addRow("Описание:", self.description_input)
        
        # Категория
        self.category_combo = QComboBox()
        self.category_combo.addItem("Выберите категорию")
        for category in self.categories:
            self.category_combo.addItem(category.name, category.id)
        form_layout.addRow("Категория:", self.category_combo)
        
        # Закупочная цена
        self.purchase_price_input = QLineEdit()
        self.purchase_price_input.setPlaceholderText("0.00")
        form_layout.addRow("Закупочная цена:", self.purchase_price_input)
        
        # Розничная цена
        self.retail_price_input = QLineEdit()
        self.retail_price_input.setPlaceholderText("0.00")
        form_layout.addRow("Розничная цена *:", self.retail_price_input)
        
        # Единица измерения
        self.unit_input = QLineEdit("шт")
        form_layout.addRow("Единица измерения:", self.unit_input)
        
        # Срок годности
        self.shelf_life_input = QLineEdit("7")
        form_layout.addRow("Срок годности (дни):", self.shelf_life_input)
        
        # Цвет
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("Например: красный, белый")
        form_layout.addRow("Цвет:", self.color_input)
        
        # Длина стебля
        self.stem_length_input = QLineEdit()
        self.stem_length_input.setPlaceholderText("Например: 50")
        form_layout.addRow("Длина стебля (см):", self.stem_length_input)
        
        # Статус
        self.active_checkbox = QCheckBox("Активен")
        self.active_checkbox.setChecked(True)
        form_layout.addRow("Статус:", self.active_checkbox)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_product)
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
        """)
    
    def load_product_data(self):
        """Загрузить данные товара"""
        if self.product:
            self.name_input.setText(self.product.name)
            self.description_input.setText(self.product.description or "")
            self.purchase_price_input.setText(str(self.product.purchase_price))
            self.retail_price_input.setText(str(self.product.retail_price))
            self.unit_input.setText(self.product.unit)
            self.shelf_life_input.setText(str(self.product.shelf_life_days))
            self.color_input.setText(self.product.color or "")
            self.stem_length_input.setText(str(self.product.stem_length_cm) if self.product.stem_length_cm else "")
            self.active_checkbox.setChecked(self.product.is_active)
            
            # Выбор категории
            if self.product.category_id:
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemData(i) == self.product.category_id:
                        self.category_combo.setCurrentIndex(i)
                        break
    
    def save_product(self):
        """Сохранить товар"""
        errors = []
        self.reset_field_styles()

        name = self.name_input.text().strip()
        if not name:
            errors.append("❌ Поле «Название» обязательно для заполнения.")
            self.name_input.setStyleSheet(self.name_input.styleSheet() + "background-color: #ffe6e6;")
        else:
            # Предпроверка дубликата до отправки на сервер (сервер вернёт 409 Conflict)
            try:
                from src.utils.validation import require_name, require_unique
                require_name(name, "Название товара")
                others = [p.name for p in getattr(self.parent(), "products", [])
                          if getattr(p, "id", None) != (self.product.id if self.product else None)]
                require_unique(name, others, "Название товара")
            except Exception as e:
                errors.append(f"❌ {e}")
                self.name_input.setStyleSheet(self.name_input.styleSheet() + "background-color: #ffe6e6;")

        retail_price_text = self.retail_price_input.text().strip()
        retail_price = None
        if not retail_price_text:
            errors.append("❌ Поле «Розничная цена» обязательно для заполнения.")
            self.retail_price_input.setStyleSheet(self.retail_price_input.styleSheet() + "background-color: #ffe6e6;")
        else:
            err = _check_decimal(retail_price_text, "Розничная цена", min_val=0.01)
            if err:
                errors.append(err)
                self.retail_price_input.setStyleSheet(self.retail_price_input.styleSheet() + "background-color: #ffe6e6;")
            else:
                retail_price = float(retail_price_text)

        from src.utils.validation import require_positive_price
        purchase_price = None
        pp_text = self.purchase_price_input.text().strip()
        if pp_text:
            try:
                require_positive_price(pp_text, "Закупочная цена")
                purchase_price = float(pp_text)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.purchase_price_input.setStyleSheet(self.purchase_price_input.styleSheet() + "background-color: #ffe6e6;")

        shelf_life = None
        sl_text = self.shelf_life_input.text().strip()
        if sl_text:
            err = _check_int(sl_text, "Срок годности", 36500, min_val=1)
            if err:
                errors.append(err)
                self.shelf_life_input.setStyleSheet(self.shelf_life_input.styleSheet() + "background-color: #ffe6e6;")
            else:
                shelf_life = int(sl_text)

        stem_length = None
        stem_text = self.stem_length_input.text().strip()
        if stem_text:
            err = _check_int(stem_text, "Длина стебля", 10000, min_val=0)
            if err:
                errors.append(err)
                self.stem_length_input.setStyleSheet(self.stem_length_input.styleSheet() + "background-color: #ffe6e6;")
            else:
                stem_length = int(stem_text)

        color_text = self.color_input.text().strip()
        if color_text:
            try:
                from src.utils.validation import require_color
                require_color(color_text)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.color_input.setStyleSheet(self.color_input.styleSheet() + "background-color: #ffe6e6;")

        from src.utils.validation import require_unit
        unit_text = self.unit_input.text().strip() or "шт"
        try:
            require_unit(unit_text)
        except Exception as e:
            errors.append(f"❌ {e}")
            self.unit_input.setStyleSheet(self.unit_input.styleSheet() + "background-color: #ffe6e6;")

        if errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(errors))
            return

        try:
            data = {
                'name': name,
                'description': self.description_input.text().strip() or None,
                'categoryId': self.category_combo.currentData(),
                'purchasePrice': purchase_price,
                'retailPrice': retail_price,
                'unit': self.unit_input.text().strip() or "шт",
                'shelfLifeDays': shelf_life or 7,
                'color': self.color_input.text().strip() or None,
                'stemLengthCm': stem_length,
                'isActive': self.active_checkbox.isChecked()
            }

            if self.product:
                self.api_service.update_product(self.product.id, **data)
                QMessageBox.information(self, "Успех", "✅ Товар успешно обновлен!")
            else:
                self.api_service.create_product(**data)
                QMessageBox.information(self, "Успех", "✅ Товар успешно добавлен!")

            self.accept()

        except Exception as e:
            dup = _check_duplicate(e, "название", name)
            if dup:
                QMessageBox.warning(self, "Ошибка", dup)
            else:
                QMessageBox.warning(self, "Ошибка", f"❌ Ошибка: {e}")

    def reset_field_styles(self):
        """Сброс стилей полей"""
        default = "padding: 5px; border: 1px solid #ddd; border-radius: 3px;"
        for inp in [self.name_input, self.description_input, self.purchase_price_input,
                     self.retail_price_input, self.unit_input, self.shelf_life_input,
                     self.color_input, self.stem_length_input]:
            inp.setStyleSheet(default)