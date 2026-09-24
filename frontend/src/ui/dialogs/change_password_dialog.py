"""
Диалог смены пароля (импортируется в main_window.change_password).
"""

from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox


class ChangePasswordDialog(QDialog):
    def __init__(self, api_service=None, parent=None):
        super().__init__(parent)
        self.api_service = api_service
        self.setWindowTitle("Сменить пароль")
        self.setMinimumWidth(350)
        layout = QFormLayout(self)
        self.old_input = QLineEdit()
        self.old_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Старый пароль:", self.old_input)
        layout.addRow("Новый пароль:", self.new_input)
        layout.addRow("Подтверждение:", self.confirm_input)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        if not self.old_input.text():
            QMessageBox.warning(self, "Ошибка", "Введите текущий пароль")
            return
        try:
            from src.utils.validation import require_password
            require_password(self.new_input.text(), "Новый пароль")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return
        if self.new_input.text() != self.confirm_input.text():
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        if self.api_service is not None:
            try:
                self.api_service.change_password(self.old_input.text(), self.new_input.text())
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сменить пароль: {e}")
                return
        self.accept()
