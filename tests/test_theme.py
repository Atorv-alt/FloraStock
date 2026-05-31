"""Модульные тесты для темы оформления (требует Qt offscreen)"""

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PyQt6.QtGui import QPalette, QFont
from src.ui.theme import FlowerWarehouseTheme, APP_NAME, APP_SUBTITLE


class TestThemeColors:
    def test_primary_green(self):
        assert FlowerWarehouseTheme.PRIMARY_GREEN.name() == "#2e7d32"

    def test_primary_blue(self):
        assert FlowerWarehouseTheme.PRIMARY_BLUE.name() == "#1e88e5"

    def test_flower_pink(self):
        assert FlowerWarehouseTheme.FLOWER_PINK.name() == "#e91e63"

    def test_flower_yellow(self):
        assert FlowerWarehouseTheme.FLOWER_YELLOW.name() == "#ffc107"

    def test_white(self):
        assert FlowerWarehouseTheme.WHITE.name() == "#ffffff"

    def test_black(self):
        assert FlowerWarehouseTheme.BLACK.name() == "#212121"

    def test_success_green(self):
        assert FlowerWarehouseTheme.SUCCESS_GREEN.name() == "#4caf50"

    def test_error_red(self):
        assert FlowerWarehouseTheme.ERROR_RED.name() == "#f44336"


class TestThemeMethods:
    def test_get_palette_returns_qpalette(self):
        palette = FlowerWarehouseTheme.get_palette()
        assert isinstance(palette, QPalette)

    def test_get_palette_has_window_color(self):
        palette = FlowerWarehouseTheme.get_palette()
        color = palette.color(QPalette.ColorRole.Window)
        assert color.name() == "#ffffff"

    def test_get_palette_button_color(self):
        palette = FlowerWarehouseTheme.get_palette()
        color = palette.color(QPalette.ColorRole.Button)
        assert color.name() == "#2e7d32"

    def test_get_font_default(self):
        font = FlowerWarehouseTheme.get_font()
        assert isinstance(font, QFont)
        assert font.pointSize() == 10
        assert font.bold() is False

    def test_get_font_bold(self):
        font = FlowerWarehouseTheme.get_font(bold=True)
        assert font.bold() is True

    def test_get_font_custom_size(self):
        font = FlowerWarehouseTheme.get_font(size=14)
        assert font.pointSize() == 14

    def test_get_header_font(self):
        font = FlowerWarehouseTheme.get_header_font()
        assert font.pointSize() == 14
        assert font.bold() is True

    def test_get_button_style_primary(self):
        style = FlowerWarehouseTheme.get_button_style("primary")
        assert "#2e7d32" in style
        assert "#FFFFFF" in style

    def test_get_button_style_secondary(self):
        style = FlowerWarehouseTheme.get_button_style("secondary")
        assert "#607d8b" in style

    def test_get_button_style_accent(self):
        style = FlowerWarehouseTheme.get_button_style("accent")
        assert "#e91e63" in style

    def test_get_button_style_warehouse(self):
        style = FlowerWarehouseTheme.get_button_style("warehouse")
        assert "#1e88e5" in style

    def test_get_button_style_unknown_fallback(self):
        style = FlowerWarehouseTheme.get_button_style("nonexistent")
        assert "#2e7d32" in style  # fallback to primary

    def test_get_toolbar_button_style(self):
        style = FlowerWarehouseTheme.get_toolbar_button_style()
        assert "#2196F3" in style
        assert "#000000" in style

    def test_get_action_button_style(self):
        style = FlowerWarehouseTheme.get_action_button_style()
        assert "#607D8B" in style
        assert "#455A64" in style

    def test_get_table_style(self):
        style = FlowerWarehouseTheme.get_table_style()
        assert "QTableWidget" in style
        assert "#2e7d32" in style  # PRIMARY_GREEN in header

    def test_get_status_style_new(self):
        style = FlowerWarehouseTheme.get_status_style("Новый")
        assert "#2e7d32" in style  # PRIMARY_GREEN

    def test_get_status_style_completed(self):
        style = FlowerWarehouseTheme.get_status_style("Выполнен")
        assert "#4caf50" in style  # SUCCESS_GREEN

    def test_get_status_style_cancelled(self):
        style = FlowerWarehouseTheme.get_status_style("Отменен")
        assert "#f44336" in style  # ERROR_RED

    def test_get_status_style_unknown_fallback(self):
        style = FlowerWarehouseTheme.get_status_style("Неизвестный")
        assert "#9e9e9e" in style  # STORAGE_GRAY

    def test_get_status_style_priority_low(self):
        style = FlowerWarehouseTheme.get_status_style("low")
        assert "#4caf50" in style

    def test_get_status_style_priority_high(self):
        style = FlowerWarehouseTheme.get_status_style("high")
        assert "#f44336" in style


class TestAppConstants:
    def test_app_name(self):
        assert APP_NAME == "🌸 FloraStock"

    def test_app_subtitle(self):
        assert APP_SUBTITLE == "Система управления складом цветов"
