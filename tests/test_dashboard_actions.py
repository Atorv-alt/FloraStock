"""Тесты быстрых действий дашборда (бывшие заглушки «в разработке», офлайн)."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QApplication

from src.ui.widgets.dashboard_widget import DashboardWidget


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_dashboard_emits_quick_action_signals(app):
    w = DashboardWidget(MagicMock())
    fired = []
    w.request_new_order.connect(lambda: fired.append("order"))
    w.request_add_product.connect(lambda: fired.append("product"))
    w.request_add_client.connect(lambda: fired.append("client"))
    w.create_new_order()
    w.add_product()
    w.add_client()
    assert fired == ["order", "product", "client"]


def _main_window_shell(dashboard):
    """Каркас вместо MainWindow (окно нельзя создать без модального логина)."""
    from types import SimpleNamespace
    return SimpleNamespace(
        tab_widget=MagicMock(),
        orders_widget=MagicMock(),
        products_widget=MagicMock(),
        clients_widget=MagicMock(),
        dashboard_widget=dashboard,
    )


def _connect_dashboard(mw, dashboard):
    """Вручную повторяем подключение из MainWindow.connect_signals."""
    from src.ui.main_window import MainWindow
    dashboard.request_new_order.connect(lambda: MainWindow.open_new_order_dialog(mw))
    dashboard.request_add_product.connect(lambda: MainWindow.open_add_product_dialog(mw))
    dashboard.request_add_client.connect(lambda: MainWindow.open_add_client_dialog(mw))


def test_main_window_connect_signals_wires_dashboard():
    """Реальный MainWindow.connect_signals должен подключать сигналы дашборда."""
    import inspect
    from src.ui.main_window import MainWindow
    src = inspect.getsource(MainWindow.connect_signals)
    assert "request_new_order.connect" in src
    assert "request_add_product.connect" in src
    assert "request_add_client.connect" in src
    assert "open_new_order_dialog" in src
    assert "open_add_product_dialog" in src
    assert "open_add_client_dialog" in src


def test_main_window_opens_order_dialog(app):
    dashboard = DashboardWidget(MagicMock())
    dashboard.refresh_data = MagicMock()
    mw = _main_window_shell(dashboard)
    _connect_dashboard(mw, dashboard)
    dashboard.create_new_order()
    mw.tab_widget.setCurrentWidget.assert_called_once_with(mw.orders_widget)
    mw.orders_widget.add_order.assert_called_once()
    dashboard.refresh_data.assert_called_once()


def test_main_window_opens_product_dialog(app):
    dashboard = DashboardWidget(MagicMock())
    dashboard.refresh_data = MagicMock()
    mw = _main_window_shell(dashboard)
    _connect_dashboard(mw, dashboard)
    dashboard.add_product()
    mw.tab_widget.setCurrentWidget.assert_called_once_with(mw.products_widget)
    mw.products_widget.add_product.assert_called_once()
    dashboard.refresh_data.assert_called_once()


def test_main_window_opens_client_dialog(app):
    dashboard = DashboardWidget(MagicMock())
    dashboard.refresh_data = MagicMock()
    mw = _main_window_shell(dashboard)
    _connect_dashboard(mw, dashboard)
    dashboard.add_client()
    mw.tab_widget.setCurrentWidget.assert_called_once_with(mw.clients_widget)
    mw.clients_widget.add_client.assert_called_once()
    dashboard.refresh_data.assert_called_once()
