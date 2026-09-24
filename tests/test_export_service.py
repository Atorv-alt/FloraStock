"""Модульные тесты для ExportService"""

import os
import tempfile
import pytest
from src.utils.export_service import ExportService


@pytest.fixture
def export_service():
    return ExportService()


@pytest.fixture
def sample_data():
    return [
        {"Товар": "Роза красная", "Количество": "100", "Цена": "150.00"},
        {"Товар": "Тюльпан жёлтый", "Количество": "200", "Цена": "80.00"},
    ]


class TestExportCSV:
    def test_export_to_csv_success(self, export_service, sample_data):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filename = f.name
        try:
            result = export_service.export_to_csv(sample_data, filename)
            assert result is True
            assert os.path.exists(filename)
            with open(filename, "r", encoding="utf-8-sig") as f:
                content = f.read()
            assert "Товар" in content
            assert "Роза красная" in content
        finally:
            os.unlink(filename)

    def test_export_to_csv_empty_data(self, export_service):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filename = f.name
        try:
            result = export_service.export_to_csv([], filename)
            assert result is False
        finally:
            os.unlink(filename)


class TestExportHTML:
    def test_export_to_html_success(self, export_service, sample_data):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            filename = f.name
        try:
            result = export_service.export_to_html("Тестовый отчёт", sample_data, filename)
            assert result is True
            assert os.path.exists(filename)
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            assert "Тестовый отчёт" in content
            assert "Роза красная" in content
            assert "<table>" in content
        finally:
            os.unlink(filename)

    def test_export_to_html_empty_data(self, export_service):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            filename = f.name
        try:
            result = export_service.export_to_html("Отчёт", [], filename)
            assert result is False
        finally:
            os.unlink(filename)


class TestExportExcel:
    def test_export_to_excel_success(self, export_service, sample_data):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            filename = f.name
        try:
            result = export_service.export_to_excel(sample_data, filename, "Тест")
            assert result is True
            assert os.path.exists(filename)
            assert os.path.getsize(filename) > 0
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_export_to_excel_empty_data(self, export_service):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            filename = f.name
        try:
            result = export_service.export_to_excel([], filename)
            assert result is False
        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestExportPDF:
    def test_export_to_pdf_success(self, export_service, sample_data):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            filename = f.name
        try:
            result = export_service.export_to_pdf("Тестовый PDF", sample_data, filename)
            assert result is True
            assert os.path.exists(filename)
            assert os.path.getsize(filename) > 0
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_cyrillic_font_registered(self):
        from reportlab.pdfbase import pdfmetrics
        from src.utils.export_service import _cyrillic_fonts
        regular, bold = _cyrillic_fonts()
        # шрифт должен быть зарегистрирован в reportlab
        assert pdfmetrics.getFont(regular) is not None
        assert pdfmetrics.getFont(bold) is not None

    def test_pdf_embeds_cyrillic_font(self, export_service):
        """Кириллица должна встраиваться TTF-сабсетом с ToUnicode (иначе ■)."""
        data = [
            {"Категория": "Товары", "Значение": "12"},
            {"Категория": "Клиенты", "Значение": "10"},
        ]
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            filename = f.name
        try:
            assert export_service.export_to_pdf("Общий отчет", data, filename) is True
            with open(filename, "rb") as f:
                raw = f.read()
            # ToUnicode CMap есть только у встроенного TTF — признак настоящего текста
            assert b"ToUnicode" in raw
            assert b"DejaVuSans" in raw or b"Arial" in raw or b"FloraSans" in raw
        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestExportWord:
    def test_export_to_word_success(self, export_service, sample_data):
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            filename = f.name
        try:
            result = export_service.export_to_word("Тестовый Word", sample_data, filename)
            assert result is True
            assert os.path.exists(filename)
            assert os.path.getsize(filename) > 0
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
