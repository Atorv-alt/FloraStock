"""
Виджет управления сотрудниками (только для администраторов)
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, 
    QLineEdit, QComboBox, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.services.api_service import ApiService
from src.models import Employee as EmployeeModel


def _check_duplicate(exc, field_name, field_value):
    from src.utils.validation import format_duplicate_error
    return format_duplicate_error(exc, field_name, field_value)


class EmployeesWidget(QWidget):
    """Виджет управления сотрудниками (только для администраторов)"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, api_service: ApiService):
        super().__init__()
        
        self.api_service = api_service
        self.employees = []
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
        
        title_label = QLabel("👥 Управление сотрудниками")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.setMinimumWidth(80)
        self.add_btn.clicked.connect(self.add_employee)
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
        self.search_input.setPlaceholderText("Введите ФИО или должность...")
        self.search_input.setMinimumWidth(150)
        self.search_input.textChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.search_input)
        
        role_label = QLabel("🔑 Уровень доступа:")
        filter_layout.addWidget(role_label)
        
        self.role_filter = QComboBox()
        self.role_filter.setMinimumWidth(120)
        self.role_filter.addItem("Все")
        self.role_filter.addItems([
            "admin", "florist", "seller", "warehouse", "courier", "purchasing"
        ])
        self.role_filter.currentTextChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.role_filter)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(7)
        self.employees_table.setHorizontalHeaderLabels([
            "ID", "ФИО", "Должность", "Телефон", "Email", "Уровень доступа", "Действия"
        ])
        
        header = self.employees_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.employees_table.setAlternatingRowColors(True)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employees_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.employees_table.setMinimumHeight(300)
        
        main_layout.addWidget(self.employees_table)
        
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
        self.employees_table.doubleClicked.connect(self.edit_employee)
    
    def refresh_data(self):
        """Обновить данные"""
        try:
            if not self.api_service.token:
                self.logger.info("Пропуск обновления данных - пользователь не авторизован")
                return
            
            self.info_label.setText("Загрузка данных...")
            
            employees_data = self.api_service.get_employees()
            self.employees = [EmployeeModel.from_dict(e) for e in employees_data]
            
            self.filter_employees()
            
            self.info_label.setText("Данные загружены")
            self.logger.info(f"Загружено {len(self.employees)} сотрудников")
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке сотрудников: {e}")
            self.info_label.setText(f"Ошибка: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить сотрудников: {e}")
    
    def filter_employees(self):
        """Отфильтровать сотрудников"""
        try:
            search_text = self.search_input.text().lower()
            role_filter = self.role_filter.currentText()
            
            filtered = []
            for emp in self.employees:
                if search_text:
                    if search_text not in emp.full_name.lower() and search_text not in (emp.position or "").lower():
                        continue
                
                if role_filter != "Все" and (emp.access_level or "") != role_filter:
                    continue
                
                filtered.append(emp)
            
            self.update_table_with_employees(filtered)
            self.total_label.setText(f"Всего: {len(filtered)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при фильтрации сотрудников: {e}")
    
    def update_table_with_employees(self, employees):
        """Обновить таблицу с указанными сотрудниками"""
        self.employees_table.setRowCount(len(employees))
        
        for row, emp in enumerate(employees):
            self.employees_table.setItem(row, 0, QTableWidgetItem(str(emp.id)))
            self.employees_table.setItem(row, 1, QTableWidgetItem(emp.full_name))
            self.employees_table.setItem(row, 2, QTableWidgetItem(emp.position or "-"))
            self.employees_table.setItem(row, 3, QTableWidgetItem(emp.phone_number or "-"))
            self.employees_table.setItem(row, 4, QTableWidgetItem(emp.email or "-"))
            
            access_item = QTableWidgetItem(emp.access_level or "-")
            if emp.access_level == "admin":
                access_item.setForeground(Qt.GlobalColor.darkRed)
            self.employees_table.setItem(row, 5, access_item)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setFixedSize(28, 24)
            edit_btn.clicked.connect(lambda checked, e=emp: self.edit_employee_by_object(e))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Удалить")
            delete_btn.setFixedSize(28, 24)
            delete_btn.clicked.connect(lambda checked, e=emp: self.delete_employee_by_object(e))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.employees_table.setCellWidget(row, 6, actions_widget)
    
    def update_table(self):
        """Обновить таблицу"""
        self.filter_employees()
    
    def add_employee(self):
        """Добавить сотрудника"""
        dialog = EmployeeDialog(self.api_service, self, None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def edit_employee(self, index):
        """Редактировать сотрудника"""
        row = index.row()
        emp_id = int(self.employees_table.item(row, 0).text())
        self.edit_employee_by_id(emp_id)
    
    def edit_employee_by_id(self, emp_id):
        """Редактировать сотрудника по ID"""
        try:
            emp = next((e for e in self.employees if e.id == emp_id), None)
            if emp:
                self.edit_employee_by_object(emp)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить сотрудника: {e}")
    
    def edit_employee_by_object(self, employee):
        """Редактировать сотрудника"""
        dialog = EmployeeDialog(self.api_service, self, employee)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def delete_employee_by_object(self, employee):
        """Удалить сотрудника"""
        if employee.access_level == "admin":
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить администратора!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить сотрудника '{employee.full_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_service.delete_employee(employee.id)
                QMessageBox.information(self, "Успех", "Сотрудник успешно удален")
                self.refresh_data()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить сотрудника: {e}")


class EmployeeDialog(QDialog):
    """Диалог добавления/редактирования сотрудника"""
    
    def __init__(self, api_service: ApiService, parent=None, employee: EmployeeModel = None):
        super().__init__(parent)
        
        self.api_service = api_service
        self.employee = employee
        
        self.setup_ui()
        self.setup_styles()
        
        if employee:
            self.load_employee_data()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("👥 Добавление сотрудника" if not self.employee else "✏️ Редактирование сотрудника")
        self.setMinimumSize(450, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        form_layout = QFormLayout()
        
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Введите ФИО сотрудника")
        form_layout.addRow("ФИО *:", self.full_name_input)
        
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Например: Флорист, Продавец")
        form_layout.addRow("Должность:", self.position_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+79001234567")
        form_layout.addRow("Телефон:", self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Уникальный логин для входа")
        form_layout.addRow("Логин *:", self.login_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Пароль *:", self.password_input)
        
        self.access_level_combo = QComboBox()
        self.access_level_combo.addItems(["florist", "seller", "warehouse", "courier", "purchasing", "admin"])
        form_layout.addRow("Уровень доступа:", self.access_level_combo)
        
        layout.addLayout(form_layout)
        
        note_label = QLabel("⚠️ Внимание: Уровень 'admin' дает полные права доступа к системе")
        note_label.setStyleSheet("color: #d32f2f; font-size: 11px;")
        layout.addWidget(note_label)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_employee)
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
    
    def load_employee_data(self):
        """Загрузить данные сотрудника"""
        if self.employee:
            self.full_name_input.setText(self.employee.full_name)
            self.position_input.setText(self.employee.position or "")
            self.phone_input.setText(self.employee.phone_number or "")
            self.email_input.setText(self.employee.email or "")
            self.login_input.setText(self.employee.login or "")
            self.password_input.setPlaceholderText("Оставьте пустым, чтобы не менять")
            
            if self.employee.access_level:
                index = self.access_level_combo.findText(self.employee.access_level)
                if index >= 0:
                    self.access_level_combo.setCurrentIndex(index)
    
    def reset_field_styles(self):
        default = "padding: 5px; border: 1px solid #ddd; border-radius: 3px;"
        for inp in [self.full_name_input, self.position_input, self.phone_input,
                     self.email_input, self.login_input, self.password_input]:
            inp.setStyleSheet(default)

    def save_employee(self):
        """Сохранить сотрудника"""
        errors = []
        self.reset_field_styles()

        full_name = self.full_name_input.text().strip()
        if not full_name:
            errors.append("❌ Поле «ФИО» обязательно для заполнения.")
            self.full_name_input.setStyleSheet(self.full_name_input.styleSheet() + "background-color: #ffe6e6;")

        login = self.login_input.text().strip()
        if not login:
            errors.append("❌ Поле «Логин» обязательно для заполнения.")
            self.login_input.setStyleSheet(self.login_input.styleSheet() + "background-color: #ffe6e6;")

        password = self.password_input.text()
        if not password and not self.employee:
            errors.append("❌ Поле «Пароль» обязательно для заполнения.")
            self.password_input.setStyleSheet(self.password_input.styleSheet() + "background-color: #ffe6e6;")

        from src.utils.validation import (
            require_access_level, require_email, require_non_empty_password,
            require_person_name, require_phone,
        )
        if full_name:
            try:
                require_person_name(full_name)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.full_name_input.setStyleSheet(self.full_name_input.styleSheet() + "background-color: #ffe6e6;")
        if password:
            try:
                require_non_empty_password(password)
            except Exception as e:
                errors.append(f"❌ {e}")
                self.password_input.setStyleSheet(self.password_input.styleSheet() + "background-color: #ffe6e6;")
        phone = self.phone_input.text().strip()
        if phone:
            try:
                require_phone(phone)
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
        try:
            require_access_level(self.access_level_combo.currentText())
        except Exception as e:
            errors.append(f"❌ {e}")

        if errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(errors))
            return

        try:
            data = {
                'fullName': full_name,
                'position': self.position_input.text().strip() or None,
                'phoneNumber': phone or None,
                'email': self.email_input.text().strip() or None,
                'loginPassword': password if password else None,
                'accessLevel': self.access_level_combo.currentText()
            }

            if self.employee:
                data['id'] = self.employee.id
                self.api_service.update_employee(self.employee.id, **data)
                QMessageBox.information(self, "Успех", "✅ Сотрудник успешно обновлен!")
            else:
                self.api_service.create_employee(**data)
                QMessageBox.information(self, "Успех", "✅ Сотрудник успешно добавлен!")

            self.accept()

        except Exception as e:
            dup = _check_duplicate(e, "логин", login)
            if dup:
                QMessageBox.warning(self, "Ошибка", dup)
            else:
                QMessageBox.warning(self, "Ошибка", f"❌ Ошибка: {e}")