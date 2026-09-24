"""
Диалог редактирования товара (листинг 2.2.4 курсовой).
Упрощенная версия для соответствия пояснительной записке,
реальная логика — в widgets/products_widget.py.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QCheckBox,
    QMessageBox, QFormLayout
)


class ProductEditDialog(QDialog):
    def __init__(self, product=None, api_service=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.api_service = api_service
        self.setup_ui()
        if self.product:
            self.fill_data()

    def setup_ui(self):
        self.setWindowTitle("📝 Редактирование товара" if self.product else "➕ Добавление товара")
        self.setFixedSize(500, 520)
        self.setModal(True)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название товара")
        form.addRow("Название *:", self.name_input)
        self.desc_input = QLineEdit()
        form.addRow("Описание:", self.desc_input)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Герберы", "Розы", "Тюльпаны", "Орхидеи", "Хризантемы", "Другое"])
        form.addRow("Категория *:", self.category_combo)
        self.purchase_price = QLineEdit()
        form.addRow("Закупочная цена:", self.purchase_price)
        self.retail_price = QLineEdit()
        form.addRow("Розничная цена *:", self.retail_price)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["шт", "кг", "м", "упаковка"])
        form.addRow("Ед. измерения:", self.unit_combo)
        self.shelf_life = QLineEdit()
        form.addRow("Срок хранения (дней):", self.shelf_life)
        self.color_combo = QComboBox()
        self.color_combo.addItems(["Красный", "Розовый", "Белый", "Желтый", "Оранжевый", "Фиолетовый", "Синий", "Разноцветный"])
        form.addRow("Цвет:", self.color_combo)
        self.stem_length = QLineEdit()
        form.addRow("Длина стебля (см):", self.stem_length)
        self.active_check = QCheckBox("Активен")
        self.active_check.setChecked(True)
        form.addRow("Статус:", self.active_check)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("✔ OK")
        ok_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def fill_data(self):
        self.name_input.setText(self.product.get("name", ""))
        self.desc_input.setText(self.product.get("description", ""))
        self.retail_price.setText(str(self.product.get("retailPrice", "")))
        self.purchase_price.setText(str(self.product.get("purchasePrice", "")))
        self.active_check.setChecked(self.product.get("isActive", True))

    def save(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название товара")
            return
        if not self.retail_price.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите розничную цену")
            return
        try:
            retail = float(self.retail_price.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Розничная цена должна быть числом")
            return
        if retail <= 0:
            QMessageBox.warning(self, "Ошибка", "Розничная цена должна быть положительным числом")
            return
        if self.purchase_price.text().strip():
            try:
                purchase = float(self.purchase_price.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Закупочная цена должна быть числом")
                return
            if purchase < 0:
                QMessageBox.warning(self, "Ошибка", "Закупочная цена не может быть отрицательной")
                return
        if self.shelf_life.text().strip():
            try:
                shelf = int(self.shelf_life.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Срок хранения должен быть целым числом")
                return
            if shelf <= 0:
                QMessageBox.warning(self, "Ошибка", "Срок хранения должен быть положительным числом")
                return
        if self.stem_length.text().strip():
            try:
                stem = int(self.stem_length.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Длина стебля должна быть целым числом")
                return
            if stem < 0:
                QMessageBox.warning(self, "Ошибка", "Длина стебля не может быть отрицательной")
                return
        # Цвет: только буквы, без цифр (поле — комбобокс с фиксированным списком,
        # но проверяем на случай редактируемого значения)
        try:
            from src.utils.validation import require_color
            color_value = self.color_combo.currentText().strip()
            if color_value:
                require_color(color_value)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return
        QMessageBox.information(self, "Успех", "Товар успешно обновлен")
        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.text().strip(),
            "category": self.category_combo.currentText(),
            "purchasePrice": float(self.purchase_price.text() or 0),
            "retailPrice": float(self.retail_price.text() or 0),
            "unit": self.unit_combo.currentText(),
            "isActive": self.active_check.isChecked(),
        }
