"""Тесты отчётов: средний чек без деления на ноль, экспорт обзора (офлайн)."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QApplication

from src.ui.widgets.reports_widget import ReportsWidget, calc_average


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _api(**kwargs):
    api = MagicMock()
    api.get_products.return_value = kwargs.get("products", [])
    api.get_clients.return_value = kwargs.get("clients", [])
    api.get_orders.return_value = kwargs.get("orders", [])
    api.get_inventory.return_value = kwargs.get("inventory", [])
    api.get_batches.return_value = kwargs.get("batches", [])
    api.get_suppliers.return_value = kwargs.get("suppliers", [])
    api.get_inventory_value.return_value = kwargs.get("inventory_value", 0.0)
    return api


def test_calc_average():
    assert calc_average(100, 4) == 25
    assert calc_average(100, 0) == 0.0
    assert calc_average(0, 0) == 0.0


def test_orders_report_empty_orders_no_error(app):
    w = ReportsWidget(_api())
    w.load_orders_report()  # раньше: ZeroDivisionError -> "Ошибка"
    text = w.orders_stats.toPlainText()
    assert "Ошибка" not in text
    assert "Всего заказов: 0" in text


def test_revenue_report_empty_orders_no_error(app):
    w = ReportsWidget(_api())
    w.load_revenue_report()  # раньше: ZeroDivisionError -> "Ошибка"
    assert "Ошибка" not in w.revenue_text.toPlainText()


def test_orders_report_with_none_amount(app):
    orders = [{"orderNumber": "ORD-001/2024", "client": None,
               "orderDate": None, "totalAmount": None, "status": "Новый"}]
    w = ReportsWidget(_api(orders=orders))
    w.load_orders_report()  # раньше: TypeError на None + 0
    assert "Ошибка" not in w.orders_stats.toPlainText()


def test_export_overview_success_shows_information(app, monkeypatch):
    info_calls = []
    warn_calls = []
    # QFileDialog/QMessageBox импортируются в методах локально,
    # поэтому патчим классы PyQt напрямую
    monkeypatch.setattr(
        "PyQt6.QtWidgets.QFileDialog.getSaveFileName",
        classmethod(lambda *a, **k: ("/tmp/overview.xlsx", "Excel Files (*.xlsx)")),
    )
    monkeypatch.setattr(
        "PyQt6.QtWidgets.QMessageBox.information",
        lambda *a, **k: info_calls.append(a),
    )
    monkeypatch.setattr(
        "PyQt6.QtWidgets.QMessageBox.warning",
        lambda *a, **k: warn_calls.append(a),
    )
    w = ReportsWidget(_api())
    w.export_service.export_to_excel = MagicMock(return_value=True)
    w.export_overview("excel")  # раньше: AttributeError на QFileDialog.parent(...).information
    assert len(info_calls) == 1
    assert warn_calls == []


def test_export_orders_failure_shows_warning(app, monkeypatch):
    warn_calls = []
    monkeypatch.setattr(
        "PyQt6.QtWidgets.QFileDialog.getSaveFileName",
        classmethod(lambda *a, **k: ("/tmp/orders.xlsx", "Excel Files (*.xlsx)")),
    )
    monkeypatch.setattr(
        "PyQt6.QtWidgets.QMessageBox.warning",
        lambda *a, **k: warn_calls.append(a),
    )
    monkeypatch.setattr(
        "PyQt6.QtWidgets.QMessageBox.information",
        lambda *a, **k: None,
    )
    w = ReportsWidget(_api())
    w.export_service.export_to_excel = MagicMock(return_value=False)
    w.export_orders("excel")  # раньше: тишина при success=False
    assert len(warn_calls) == 1
