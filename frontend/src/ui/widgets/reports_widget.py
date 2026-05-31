"""
Виджет отчетов и статистики
"""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton,
    QTextEdit, QTabWidget, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from src.services.api_service import ApiService
from src.utils.export_service import ExportService


class ReportsWidget(QWidget):
    """Виджет отчетов"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, api_service: ApiService):
        super().__init__()
        
        self.api_service = api_service
        self.export_service = ExportService()
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
        
        title_label = QLabel("📊 Отчеты и статистика")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Обновить все")
        self.refresh_btn.setMinimumWidth(120)
        self.refresh_btn.setStyleSheet("background-color: #4CAF50; color: #FFFFFF; padding: 8px 16px; border: none; border-radius: 4px;")
        self.refresh_btn.clicked.connect(self.refresh_all)
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        tabs = QTabWidget()
        
        tabs.addTab(self.create_overview_tab(), "📈 Обзор")
        tabs.addTab(self.create_orders_report_tab(), "🛒 Заказы")
        tabs.addTab(self.create_inventory_report_tab(), "📋 Склад")
        tabs.addTab(self.create_revenue_report_tab(), "💰 Выручка")
        
        main_layout.addWidget(tabs)
    
    def create_overview_tab(self):
        """Вкладка общего обзора"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QHBoxLayout()
        title = QLabel("📊 Общая статистика")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        
        excel_btn = QPushButton("📊 Excel")
        excel_btn.setStyleSheet("background-color: #217346; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        excel_btn.clicked.connect(lambda: self.export_overview('excel'))
        header.addWidget(excel_btn)
        
        pdf_btn = QPushButton("📄 PDF")
        pdf_btn.setStyleSheet("background-color: #FF5722; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        pdf_btn.clicked.connect(lambda: self.export_overview('pdf'))
        header.addWidget(pdf_btn)
        
        word_btn = QPushButton("📝 Word")
        word_btn.setStyleSheet("background-color: #2B579A; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        word_btn.clicked.connect(lambda: self.export_overview('word'))
        header.addWidget(word_btn)
        
        layout.addLayout(header)
        
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        self.overview_text.setStyleSheet("background-color: #f5f5f5; padding: 15px; border-radius: 8px;")
        layout.addWidget(self.overview_text)
        
        self.load_overview()
        return widget
    
    def load_overview(self):
        """Загрузка общей статистики"""
        try:
            products = self.api_service.get_products()
            clients = self.api_service.get_clients()
            orders = self.api_service.get_orders()
            inventory = self.api_service.get_inventory()
            batches = self.api_service.get_batches()
            suppliers = self.api_service.get_suppliers()
            
            low_stock = [i for i in inventory if i.get('quantity', 0) <= 10]
            
            self.overview_text.setHtml(f"""
            <style>
                .stat-card {{ background: white; padding: 15px; border-radius: 8px; margin: 5px; border-left: 4px solid #4CAF50; }}
                .stat-title {{ color: #666; font-size: 12px; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
                .stat-row {{ display: flex; flex-wrap: wrap; }}
            </style>
            <div class="stat-row">
                <div class="stat-card" style="flex: 1; min-width: 150px;">
                    <div class="stat-title">🌺 Товары</div>
                    <div class="stat-value">{len(products)}</div>
                </div>
                <div class="stat-card" style="flex: 1; min-width: 150px;">
                    <div class="stat-title">👥 Клиенты</div>
                    <div class="stat-value">{len(clients)}</div>
                </div>
                <div class="stat-card" style="flex: 1; min-width: 150px;">
                    <div class="stat-title">🛒 Заказы</div>
                    <div class="stat-value">{len(orders)}</div>
                </div>
                <div class="stat-card" style="flex: 1; min-width: 150px;">
                    <div class="stat-title">📋 Склад</div>
                    <div class="stat-value">{len(inventory)}</div>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <h4 style="color: #4CAF50; margin-bottom: 10px;">📦 Детализация</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f5f5f5;">
                        <td style="padding: 10px; border: 1px solid #ddd;">Партии</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{len(batches)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">Поставщики</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{len(suppliers)}</td>
                    </tr>
                    <tr style="background: #f5f5f5;">
                        <td style="padding: 10px; border: 1px solid #ddd;">Низкий остаток (≤10)</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; color: {'#f44336' if len(low_stock) > 0 else '#4CAF50'};">{len(low_stock)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">Завершенных заказов</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{len([o for o in orders if o.get('status') in ['Выполнен', 'Доставлен']])}</td>
                    </tr>
                    <tr style="background: #f5f5f5;">
                        <td style="padding: 10px; border: 1px solid #ddd;">Заказов в процессе</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{len([o for o in orders if o.get('status') == 'В обработке'])}</td>
                    </tr>
                </table>
            </div>
            """)
        except Exception as e:
            self.overview_text.setHtml(f"<b style='color: #f44336;'>Ошибка загрузки:</b> {e}")
    
    def export_overview(self, fmt):
        """Экспорт общего отчета"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            products = self.api_service.get_products()
            clients = self.api_service.get_clients()
            orders = self.api_service.get_orders()
            inventory = self.api_service.get_inventory()
            batches = self.api_service.get_batches()
            suppliers = self.api_service.get_suppliers()
            
            data = [
                {"Категория": "Товары", "Значение": str(len(products))},
                {"Категория": "Клиенты", "Значение": str(len(clients))},
                {"Категория": "Заказы", "Значение": str(len(orders))},
                {"Категория": "Склад", "Значение": str(len(inventory))},
                {"Категория": "Партии", "Значение": str(len(batches))},
                {"Категория": "Поставщики", "Значение": str(len(suppliers))}
            ]
            
            filters = {'excel': ("Excel Files (*.xlsx)", ".xlsx"), 'pdf': ("PDF Files (*.pdf)", ".pdf"), 'word': ("Word Files (*.docx)", ".docx")}
            
            filename, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", f"overview_{datetime.now().strftime('%Y%m%d')}", filters[fmt][0])
            
            if filename:
                if not filename.endswith(filters[fmt][1]):
                    filename += filters[fmt][1]
                
                success = False
                if fmt == 'excel':
                    success = self.export_service.export_to_excel(data, filename, "Обзор")
                elif fmt == 'pdf':
                    success = self.export_service.export_to_pdf("Общий отчет", data, filename)
                elif fmt == 'word':
                    success = self.export_service.export_to_word("Общий отчет", data, filename)
                
                if success:
                    QFileDialog.parent(self).information(self, "Успех", f"Отчет сохранен:\n{filename}")
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Ошибка", "Установите необходимые библиотеки (openpyxl, reportlab, python-docx)")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", f"Ошибка экспорта: {e}")
    
    def create_orders_report_tab(self):
        """Вкладка отчета по заказам"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QHBoxLayout()
        title = QLabel("🛒 Анализ заказов")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        
        excel_btn = QPushButton("📊 Excel")
        excel_btn.setStyleSheet("background-color: #217346; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        excel_btn.clicked.connect(lambda: self.export_orders('excel'))
        header.addWidget(excel_btn)
        
        pdf_btn = QPushButton("📄 PDF")
        pdf_btn.setStyleSheet("background-color: #FF5722; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        pdf_btn.clicked.connect(lambda: self.export_orders('pdf'))
        header.addWidget(pdf_btn)
        
        word_btn = QPushButton("📝 Word")
        word_btn.setStyleSheet("background-color: #2B579A; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        word_btn.clicked.connect(lambda: self.export_orders('word'))
        header.addWidget(word_btn)
        
        layout.addLayout(header)
        
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Номер", "Клиент", "Дата", "Сумма", "Статус"])
        self.orders_table.setAlternatingRowColors(True)
        layout.addWidget(self.orders_table)
        
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: #f5f5f5; border-radius: 8px; padding: 10px;")
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📊 Статистика")
        stats_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        stats_layout.addWidget(stats_title)
        
        self.orders_stats = QTextEdit()
        self.orders_stats.setReadOnly(True)
        self.orders_stats.setMaximumHeight(100)
        stats_layout.addWidget(self.orders_stats)
        
        layout.addWidget(stats_frame)
        
        self.load_orders_report()
        return widget
    
    def load_orders_report(self):
        """Загрузка отчета по заказам"""
        try:
            orders = self.api_service.get_orders()
            self.orders_table.setRowCount(len(orders))
            total = 0
            statuses = {}
            
            for i, order in enumerate(orders[:100]):
                self.orders_table.setItem(i, 0, QTableWidgetItem(str(order.get('orderNumber', ''))))
                
                client = order.get('client', {})
                client_name = client.get('fullName', 'Неизвестен') if isinstance(client, dict) else str(client)
                self.orders_table.setItem(i, 1, QTableWidgetItem(client_name))
                
                date = order.get('orderDate', '')
                if date:
                    try:
                        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                        date = dt.strftime("%d.%m.%Y")
                    except:
                        pass
                self.orders_table.setItem(i, 2, QTableWidgetItem(str(date)))
                
                amount = order.get('totalAmount', 0)
                total += amount
                self.orders_table.setItem(i, 3, QTableWidgetItem(f"₽{amount:,.2f}"))
                
                status = order.get('status', 'Неизвестен')
                self.orders_table.setItem(i, 4, QTableWidgetItem(status))
                statuses[status] = statuses.get(status, 0) + 1
            
            status_text = "<br>".join([f"• {k}: <b>{v}</b> шт." for k, v in statuses.items()])
            self.orders_stats.setHtml(f"""
            <b>Всего заказов:</b> {len(orders)} | 
            <b>Общая сумма:</b> <span style="color: #4CAF50;">₽{total:,.2f}</span> | 
            <b>Средний чек:</b> ₽{total/len(orders):,.2f}
            <br><br>{status_text}
            """)
        except Exception as e:
            self.orders_stats.setHtml(f"<b style='color: #f44336;'>Ошибка:</b> {e}")
    
    def export_orders(self, fmt):
        """Экспорт отчета по заказам"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            orders = self.api_service.get_orders()
            data = []
            
            for order in orders:
                client = order.get('client', {})
                client_name = client.get('fullName', '') if isinstance(client, dict) else str(client)
                
                date = order.get('orderDate', '')
                if date:
                    try:
                        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                        date = dt.strftime("%d.%m.%Y")
                    except:
                        pass
                
                data.append({
                    "Номер заказа": order.get('orderNumber', ''),
                    "Клиент": client_name,
                    "Дата": str(date),
                    "Сумма": f"{order.get('totalAmount', 0):.2f}",
                    "Статус": order.get('status', '')
                })
            
            filters = {'excel': ("Excel Files (*.xlsx)", ".xlsx"), 'pdf': ("PDF Files (*.pdf)", ".pdf"), 'word': ("Word Files (*.docx)", ".docx")}
            
            filename, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", f"orders_{datetime.now().strftime('%Y%m%d')}", filters[fmt][0])
            
            if filename:
                if not filename.endswith(filters[fmt][1]):
                    filename += filters[fmt][1]
                
                success = False
                if fmt == 'excel':
                    success = self.export_service.export_to_excel(data, filename, "Заказы")
                elif fmt == 'pdf':
                    success = self.export_service.export_to_pdf("Отчет по заказам", data, filename)
                elif fmt == 'word':
                    success = self.export_service.export_to_word("Отчет по заказам", data, filename)
                
                if success:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Успех", f"Отчет сохранен:\n{filename}")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", f"Ошибка экспорта: {e}")
    
    def create_inventory_report_tab(self):
        """Вкладка отчета по складу"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QHBoxLayout()
        title = QLabel("📋 Состояние склада")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        
        excel_btn = QPushButton("📊 Excel")
        excel_btn.setStyleSheet("background-color: #217346; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        excel_btn.clicked.connect(lambda: self.export_inventory('excel'))
        header.addWidget(excel_btn)
        
        pdf_btn = QPushButton("📄 PDF")
        pdf_btn.setStyleSheet("background-color: #FF5722; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        pdf_btn.clicked.connect(lambda: self.export_inventory('pdf'))
        header.addWidget(pdf_btn)
        
        word_btn = QPushButton("📝 Word")
        word_btn.setStyleSheet("background-color: #2B579A; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        word_btn.clicked.connect(lambda: self.export_inventory('word'))
        header.addWidget(word_btn)
        
        layout.addLayout(header)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "Товар", "Количество", "Место хранения", "Температура", "Статус"])
        self.inventory_table.setAlternatingRowColors(True)
        layout.addWidget(self.inventory_table)
        
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: #f5f5f5; border-radius: 8px; padding: 10px;")
        stats_layout = QHBoxLayout(stats_frame)
        
        self.low_stock_label = QLabel("⚠️ Низкий остаток (≤10): <b>0</b>")
        stats_layout.addWidget(self.low_stock_label)
        
        stats_layout.addStretch()
        
        self.total_value_label = QLabel("💰 Общая стоимость: <b>₽0</b>")
        stats_layout.addWidget(self.total_value_label)
        
        layout.addWidget(stats_frame)
        
        self.load_inventory_report()
        return widget
    
    def load_inventory_report(self):
        """Загрузка отчета по складу"""
        try:
            inventory = self.api_service.get_inventory()
            products = self.api_service.get_products()
            product_map = {p.get('id'): p.get('name', 'Неизвестен') for p in products}
            
            low_stock = 0
            self.inventory_table.setRowCount(len(inventory))
            
            for i, item in enumerate(inventory):
                self.inventory_table.setItem(i, 0, QTableWidgetItem(str(item.get('id', ''))))
                
                product_name = product_map.get(item.get('productId'), 'Неизвестен')
                self.inventory_table.setItem(i, 1, QTableWidgetItem(product_name))
                
                quantity = item.get('quantity', 0)
                qty_item = QTableWidgetItem(str(quantity))
                if quantity <= 10:
                    low_stock += 1
                    qty_item.setBackground(QColor(255, 200, 200))
                self.inventory_table.setItem(i, 2, qty_item)
                
                self.inventory_table.setItem(i, 3, QTableWidgetItem(item.get('storageLocation', '-')))
                self.inventory_table.setItem(i, 4, QTableWidgetItem(item.get('storageTemperature', '-')))
                
                if quantity == 0:
                    status = "❌ Нет"
                elif quantity <= 10:
                    status = "⚠️ Мало"
                else:
                    status = "✅ В наличии"
                self.inventory_table.setItem(i, 5, QTableWidgetItem(status))
            
            self.low_stock_label.setText(f"⚠️ Низкий остаток (≤10): <b style='color: #f44336;'>{low_stock}</b>")
            
            inventory_value = self.api_service.get_inventory_value()
            self.total_value_label.setText(f"💰 Общая стоимость: <b style='color: #4CAF50;'>₽{inventory_value:,.2f}</b>")
        except Exception as e:
            self.low_stock_label.setText(f"⚠️ Низкий остаток: <b style='color: #f44336;'>Ошибка</b>")
    
    def export_inventory(self, fmt):
        """Экспорт отчета по складу"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            inventory = self.api_service.get_inventory()
            products = self.api_service.get_products()
            product_map = {p.get('id'): p.get('name', 'Неизвестен') for p in products}
            
            data = []
            for item in inventory:
                quantity = item.get('quantity', 0)
                status = "Нет" if quantity == 0 else ("Мало" if quantity <= 10 else "В наличии")
                
                data.append({
                    "ID": str(item.get('id', '')),
                    "Товар": product_map.get(item.get('productId'), 'Неизвестен'),
                    "Количество": str(quantity),
                    "Место хранения": item.get('storageLocation', '-'),
                    "Температура": item.get('storageTemperature', '-'),
                    "Статус": status
                })
            
            filters = {'excel': ("Excel Files (*.xlsx)", ".xlsx"), 'pdf': ("PDF Files (*.pdf)", ".pdf"), 'word': ("Word Files (*.docx)", ".docx")}
            
            filename, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", f"inventory_{datetime.now().strftime('%Y%m%d')}", filters[fmt][0])
            
            if filename:
                if not filename.endswith(filters[fmt][1]):
                    filename += filters[fmt][1]
                
                success = False
                if fmt == 'excel':
                    success = self.export_service.export_to_excel(data, filename, "Склад")
                elif fmt == 'pdf':
                    success = self.export_service.export_to_pdf("Отчет по складу", data, filename)
                elif fmt == 'word':
                    success = self.export_service.export_to_word("Отчет по складу", data, filename)
                
                if success:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Успех", f"Отчет сохранен:\n{filename}")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", f"Ошибка экспорта: {e}")
    
    def create_revenue_report_tab(self):
        """Вкладка отчета по выручке"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QHBoxLayout()
        title = QLabel("💰 Финансовая статистика")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        
        excel_btn = QPushButton("📊 Excel")
        excel_btn.setStyleSheet("background-color: #217346; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        excel_btn.clicked.connect(lambda: self.export_revenue('excel'))
        header.addWidget(excel_btn)
        
        pdf_btn = QPushButton("📄 PDF")
        pdf_btn.setStyleSheet("background-color: #FF5722; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        pdf_btn.clicked.connect(lambda: self.export_revenue('pdf'))
        header.addWidget(pdf_btn)
        
        word_btn = QPushButton("📝 Word")
        word_btn.setStyleSheet("background-color: #2B579A; color: #FFFFFF; padding: 6px 12px; border: none; border-radius: 4px;")
        word_btn.clicked.connect(lambda: self.export_revenue('word'))
        header.addWidget(word_btn)
        
        layout.addLayout(header)
        
        self.revenue_text = QTextEdit()
        self.revenue_text.setReadOnly(True)
        self.revenue_text.setStyleSheet("background-color: #f5f5f5; padding: 15px; border-radius: 8px;")
        layout.addWidget(self.revenue_text)
        
        self.load_revenue_report()
        return widget
    
    def load_revenue_report(self):
        """Загрузка финансового отчета"""
        try:
            orders = self.api_service.get_orders()
            inventory_value = self.api_service.get_inventory_value()
            
            total_revenue = sum(o.get('totalAmount', 0) for o in orders)
            completed = sum(1 for o in orders if o.get('status') in ['Выполнен', 'Доставлен'])
            in_progress = sum(1 for o in orders if o.get('status') == 'В обработке')
            
            self.revenue_text.setHtml(f"""
            <style>
                .metric {{ display: flex; justify-content: space-between; padding: 15px; background: white; margin: 5px 0; border-radius: 8px; }}
                .metric-value {{ font-size: 20px; font-weight: bold; color: #4CAF50; }}
                .metric-label {{ color: #666; }}
            </style>
            
            <h3 style="color: #4CAF50;">💵 Выручка</h3>
            <div class="metric">
                <span class="metric-label">Общая выручка</span>
                <span class="metric-value">₽{total_revenue:,.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Средний чек</span>
                <span style="font-size: 20px; font-weight: bold; color: #2196F3;">₽{total_revenue/len(orders):,.2f}</span>
            </div>
            
            <h3 style="color: #4CAF50; margin-top: 20px;">📊 Заказы</h3>
            <div class="metric">
                <span class="metric-label">Всего заказов</span>
                <span style="font-size: 20px; font-weight: bold;">{len(orders)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Завершено</span>
                <span style="font-size: 20px; font-weight: bold; color: #4CAF50;">{completed}</span>
            </div>
            <div class="metric">
                <span class="metric-label">В процессе</span>
                <span style="font-size: 20px; font-weight: bold; color: #FF9800;">{in_progress}</span>
            </div>
            
            <h3 style="color: #4CAF50; margin-top: 20px;">📦 Склад</h3>
            <div class="metric">
                <span class="metric-label">Стоимость склада</span>
                <span style="font-size: 20px; font-weight: bold; color: #9C27B0;">₽{inventory_value:,.2f}</span>
            </div>
            """)
        except Exception as e:
            self.revenue_text.setHtml(f"<b style='color: #f44336;'>Ошибка:</b> {e}")
    
    def export_revenue(self, fmt):
        """Экспорт финансового отчета"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            orders = self.api_service.get_orders()
            inventory_value = self.api_service.get_inventory_value()
            
            total_revenue = sum(o.get('totalAmount', 0) for o in orders)
            completed = sum(1 for o in orders if o.get('status') in ['Выполнен', 'Доставлен'])
            in_progress = sum(1 for o in orders if o.get('status') == 'В обработке')
            
            data = [
                {"Показатель": "Общая выручка", "Значение": f"₽{total_revenue:,.2f}"},
                {"Показатель": "Средний чек", "Значение": f"₽{total_revenue/len(orders):,.2f}" if orders else "₽0"},
                {"Показатель": "Всего заказов", "Значение": str(len(orders))},
                {"Показатель": "Завершено", "Значение": str(completed)},
                {"Показатель": "В процессе", "Значение": str(in_progress)},
                {"Показатель": "Стоимость склада", "Значение": f"₽{inventory_value:,.2f}"}
            ]
            
            filters = {'excel': ("Excel Files (*.xlsx)", ".xlsx"), 'pdf': ("PDF Files (*.pdf)", ".pdf"), 'word': ("Word Files (*.docx)", ".docx")}
            
            filename, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", f"revenue_{datetime.now().strftime('%Y%m%d')}", filters[fmt][0])
            
            if filename:
                if not filename.endswith(filters[fmt][1]):
                    filename += filters[fmt][1]
                
                success = False
                if fmt == 'excel':
                    success = self.export_service.export_to_excel(data, filename, "Выручка")
                elif fmt == 'pdf':
                    success = self.export_service.export_to_pdf("Финансовый отчет", data, filename)
                elif fmt == 'word':
                    success = self.export_service.export_to_word("Финансовый отчет", data, filename)
                
                if success:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Успех", f"Отчет сохранен:\n{filename}")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", f"Ошибка экспорта: {e}")
    
    def refresh_data(self):
        """Обновить данные"""
        self.refresh_all()

    def refresh_all(self):
        """Обновить все отчеты"""
        self.load_overview()
        self.load_orders_report()
        self.load_inventory_report()
        self.load_revenue_report()

    def setup_styles(self):
        """Настройка стилей"""
        self.setStyleSheet("""
            QLabel { color: #333333; }
            QPushButton { padding: 6px 12px; border: none; border-radius: 4px; font-weight: bold; }
            QTableWidget { background: white; border-radius: 8px; }
            QHeaderView::section { background-color: #4CAF50; color: white; padding: 8px; font-weight: bold; }
        """)
    
    def connect_signals(self):
        """Подключение сигналов"""
        self.data_updated.connect(self.refresh_all)