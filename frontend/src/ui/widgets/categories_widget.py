"""
Виджет управления категориями (раздел 2.4 курсовой: пункт меню «Категории»).
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.services.api_service import ApiService


class CategoriesWidget(QWidget):
    """Виджет управления категориями товаров"""

    data_updated = pyqtSignal()

    def __init__(self, api_service: ApiService):
        super().__init__()
        self.api_service = api_service
        self.categories = []
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel("📁 Управление категориями")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        self.add_btn = QPushButton("➕ Добавить")
        self.refresh_btn = QPushButton("🔄 Обновить")
        header.addWidget(self.add_btn)
        header.addWidget(self.refresh_btn)
        main_layout.addLayout(header)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название категории...")
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        main_layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Описание"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        main_layout.addWidget(self.table)

        status = QHBoxLayout()
        status.addWidget(QLabel("Данные загружены"))
        status.addStretch()
        self.total_label = QLabel("Всего: 0")
        status.addWidget(self.total_label)
        main_layout.addLayout(status)

    def connect_signals(self):
        self.add_btn.clicked.connect(self.add_category)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.search_input.textChanged.connect(self.apply_filter)

    def refresh_data(self):
        try:
            if not self.api_service.token:
                self.categories = []
                self.apply_filter()
                return
            data = self.api_service.get_categories()
            self.categories = data if isinstance(data, list) else []
        except Exception as e:
            self.logger.error(f"Ошибка загрузки категорий: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить категории: {e}")
            self.categories = []
        self.apply_filter()

    def apply_filter(self):
        query = self.search_input.text().strip().lower()
        rows = [c for c in self.categories if query in str(c.get("name", "")).lower()] if query else list(self.categories)
        self.table.setRowCount(len(rows))
        for r, c in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(c.get("id", ""))))
            self.table.setItem(r, 1, QTableWidgetItem(str(c.get("name", ""))))
            self.table.setItem(r, 2, QTableWidgetItem(str(c.get("description", ""))))
        self.total_label.setText(f"Всего: {len(rows)}")

    def add_category(self):
        existing = [str(c.get("name", "")) for c in self.categories]
        dialog = CategoryEditDialog(parent=self, existing_names=existing)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                self.api_service.create_category(data["name"], data.get("description"))
                self.refresh_data()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось добавить: {e}")


class CategoryEditDialog(QDialog):
    def __init__(self, category=None, parent=None, existing_names=None):
        super().__init__(parent)
        self.category = category or {}
        self.existing_names = [n for n in (existing_names or [])
                               if n.strip().lower() != str(self.category.get("name", "")).strip().lower()]
        self.setWindowTitle("Добавление категории")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.name_input = QLineEdit(self.category.get("name", ""))
        self.desc_input = QLineEdit(self.category.get("description", ""))
        layout.addRow("Название *:", self.name_input)
        layout.addRow("Описание:", self.desc_input)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название категории")
            return
        try:
            from src.utils.validation import require_name, require_unique
            require_name(name, "Наименование категории")
            require_unique(name, self.existing_names, "Наименование категории")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return
        self.accept()

    def get_data(self):
        return {"name": self.name_input.text().strip(), "description": self.desc_input.text().strip()}
