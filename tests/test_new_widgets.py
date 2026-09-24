"""Тесты новых модулей: categories_widget, product_edit_dialog, change_password_dialog (офлайн)."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QApplication, QDialog

from src.ui.widgets.categories_widget import CategoriesWidget, CategoryEditDialog
from src.ui.dialogs.product_edit_dialog import ProductEditDialog
from src.ui.dialogs.change_password_dialog import ChangePasswordDialog


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_category_dialog_rejects_empty_name(app, monkeypatch):
    d = CategoryEditDialog()
    monkeypatch.setattr("src.ui.widgets.categories_widget.QMessageBox.warning", lambda *a, **k: None)
    assert d.name_input.text() == ""
    d.validate_and_accept()
    assert d.result() == 0  # диалог не закрыт


def test_category_dialog_accepts_valid(app):
    d = CategoryEditDialog()
    d.name_input.setText("Розы")
    d.desc_input.setText("desc")
    d.validate_and_accept()
    assert d.result() == QDialog.DialogCode.Accepted
    assert d.get_data() == {"name": "Розы", "description": "desc"}


def test_product_dialog_requires_name_and_price(app, monkeypatch):
    monkeypatch.setattr("src.ui.dialogs.product_edit_dialog.QMessageBox.warning", lambda *a, **k: None)
    monkeypatch.setattr("src.ui.dialogs.product_edit_dialog.QMessageBox.information", lambda *a, **k: None)
    d = ProductEditDialog()
    d.save()
    assert d.result() == 0
    d.name_input.setText("Роза")
    d.save()
    assert d.result() == 0
    d.retail_price.setText("300")
    d.save()
    assert d.result() == QDialog.DialogCode.Accepted


def test_change_password_mismatch(app, monkeypatch):
    monkeypatch.setattr("src.ui.dialogs.change_password_dialog.QMessageBox.warning", lambda *a, **k: None)
    d = ChangePasswordDialog(api_service=MagicMock())
    d.old_input.setText("oldpass")
    d.new_input.setText("aaa111")
    d.confirm_input.setText("bbb222")
    d.validate_and_accept()
    assert d.result() == 0


def test_change_password_too_short(app, monkeypatch):
    monkeypatch.setattr("src.ui.dialogs.change_password_dialog.QMessageBox.warning", lambda *a, **k: None)
    d = ChangePasswordDialog(api_service=MagicMock())
    d.old_input.setText("oldpass")
    d.new_input.setText("abc")
    d.confirm_input.setText("abc")
    d.validate_and_accept()
    assert d.result() == 0


def test_change_password_calls_api(app):
    api = MagicMock()
    d = ChangePasswordDialog(api_service=api)
    d.old_input.setText("oldpass")
    d.new_input.setText("newpass1")
    d.confirm_input.setText("newpass1")
    d.validate_and_accept()
    api.change_password.assert_called_once_with("oldpass", "newpass1")
    assert d.result() == QDialog.DialogCode.Accepted


def test_change_password_api_error_keeps_dialog(app, monkeypatch):
    monkeypatch.setattr("src.ui.dialogs.change_password_dialog.QMessageBox.critical", lambda *a, **k: None)
    api = MagicMock()
    api.change_password.side_effect = Exception("bad current")
    d = ChangePasswordDialog(api_service=api)
    d.old_input.setText("oldpass")
    d.new_input.setText("newpass1")
    d.confirm_input.setText("newpass1")
    d.validate_and_accept()
    assert d.result() == 0


def test_categories_widget_loads_from_api(app):
    api = MagicMock()
    api.get_categories.return_value = [
        {"id": 1, "name": "Розы", "description": "розы"},
        {"id": 2, "name": "Тюльпаны", "description": "тюльпаны"},
    ]
    w = CategoriesWidget(api)
    w.refresh_data()
    api.get_categories.assert_called_once()
    assert len(w.categories) == 2
    assert w.total_label.text() == "Всего: 2"


def test_categories_widget_empty_on_api_error(app, monkeypatch):
    monkeypatch.setattr("src.ui.widgets.categories_widget.QMessageBox.warning", lambda *a, **k: None)
    api = MagicMock()
    api.get_categories.side_effect = Exception("no connection")
    w = CategoriesWidget(api)
    w.refresh_data()
    assert w.categories == []
    assert w.total_label.text() == "Всего: 0"


def test_db_dialog_api_url_field(app):
    from src.ui.dialogs.database_connection_dialog import DatabaseConnectionDialog
    config = MagicMock()
    config.api_base_url = "http://srv:9000/api"
    config.db_host = "localhost"
    config.db_port = "5432"
    config.db_name = "sclad"
    config.db_user = "postgres"
    config.db_password = ""
    d = DatabaseConnectionDialog(config)
    assert d.api_url_input.text() == "http://srv:9000/api"
    d.api_url_input.setText("http://srv:9000/api/")
    assert d.get_api_url() == "http://srv:9000/api"


def test_employees_filter_by_access_level(app):
    from src.models import Employee
    from src.ui.widgets.employees_widget import EmployeesWidget
    w = EmployeesWidget(MagicMock())
    w.employees = [
        Employee(id=1, full_name="Анна", access_level="florist"),
        Employee(id=2, full_name="Борис", access_level="courier"),
    ]
    w.role_filter.setCurrentText("florist")
    w.filter_employees()
    assert w.employees_table.rowCount() == 1
    assert w.employees_table.item(0, 1).text() == "Анна"
    w.role_filter.setCurrentText("Все")
    w.filter_employees()
    assert w.employees_table.rowCount() == 2


def test_client_dialog_create_maps_fields(app, monkeypatch):
    """save_client должен вызывать create_client(full_name, phone, email) позиционно."""
    from src.ui.widgets.clients_widget import ClientDialog
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", lambda *a, **k: None)
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.information", lambda *a, **k: None)
    api = MagicMock()
    api.create_client.return_value = {"id": 1}
    d = ClientDialog(api)
    d.full_name_input.setText("Иван Иванов")
    d.phone_input.setText("+79161234567")
    d.email_input.setText("ivan@mail.ru")
    d.save_client()
    api.create_client.assert_called_once_with("Иван Иванов", "+79161234567", "ivan@mail.ru")
    assert d.result() == QDialog.DialogCode.Accepted


def test_cancel_order_calls_api(app, monkeypatch):
    """Отмена заказа должна реально удалять его через API, а не только показывать успех."""
    from datetime import date
    from decimal import Decimal
    from src.models import Order
    from src.ui.widgets.orders_widget import OrdersWidget
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", lambda *a, **k: None)
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.information", lambda *a, **k: None)
    monkeypatch.setattr(
        "PyQt6.QtWidgets.QMessageBox.question",
        lambda *a, **k: __import__("PyQt6.QtWidgets", fromlist=["QMessageBox"]).QMessageBox.StandardButton.Yes,
    )
    api = MagicMock()
    api.delete_order.return_value = True
    w = OrdersWidget(api)
    w.refresh_data = MagicMock()
    order = Order(id=5, order_number="ORD-001/2024", order_date=date(2024, 1, 20),
                  status="Новый", total_amount=Decimal("100"))
    w.cancel_order_by_object(order)
    api.delete_order.assert_called_once_with(5)
