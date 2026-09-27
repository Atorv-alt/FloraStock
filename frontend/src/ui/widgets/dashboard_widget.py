"""
Виджет панели управления
"""

import logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGridLayout, QFrame, QPushButton, QMessageBox,
    QDialog, QTextEdit, QTableWidget, QTableWidgetItem,
    QTabWidget, QDateEdit, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from src.services.api_service import ApiService
from src.utils.config import Config
from src.utils.export_service import ExportService


class ReportsDialog(QDialog):
    """Диалоговое окно с расширенными отчетами"""
    
    def __init__(self, api_service, parent=None):
        super().__init__(parent)
        self.api_service = api_service
        self.export_service = ExportService()
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("📊 Отчеты и статистика")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        tabs.addTab(self.create_overview_tab(), "📈 Обзор")
        tabs.addTab(self.create_orders_report_tab(), "🛒 Заказы")
        tabs.addTab(self.create_inventory_report_tab(), "📋 Склад")
        tabs.addTab(self.create_revenue_report_tab(), "💰 Выручка")
        
        layout.addWidget(tabs)
    
    def create_overview_tab(self):
        """Вкладка общего обзора"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("📊 Общая статистика")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        self.overview_text.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        layout.addWidget(self.overview_text)
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        refresh_btn.clicked.connect(self.load_overview)
        btn_layout.addWidget(refresh_btn)
        
        export_label = QLabel("Экспорт:")
        btn_layout.addWidget(export_label)
        
        excel_btn = QPushButton("📊 Excel")
        excel_btn.setStyleSheet("background-color: #217346; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        excel_btn.clicked.connect(lambda: self.export_overview('excel'))
        btn_layout.addWidget(excel_btn)
        
        pdf_btn = QPushButton("📄 PDF")
        pdf_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        pdf_btn.clicked.connect(lambda: self.export_overview('pdf'))
        btn_layout.addWidget(pdf_btn)
        
        word_btn = QPushButton("📝 Word")
        word_btn.setStyleSheet("background-color: #2B579A; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        word_btn.clicked.connect(lambda: self.export_overview('word'))
        btn_layout.addWidget(word_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.load_overview()
        return widget
    
    def export_overview(self, fmt):
        """Экспорт общего отчета"""
        try:
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
            
            filters = {
                'excel': ("Excel Files (*.xlsx)", ".xlsx"),
                'pdf': ("PDF Files (*.pdf)", ".pdf"),
                'word': ("Word Files (*.docx)", ".docx")
            }
            
            from PyQt6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить отчет",
                f"overview_report_{datetime.now().strftime('%Y%m%d')}",
                filters[fmt][0]
            )
            
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
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Успех", f"Отчет сохранен:\n{filename}")
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Ошибка", "Не удалось сохранить отчет. Убедитесь, что установлены необходимые библиотеки.")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", f"Ошибка экспорта: {e}")
    
    def load_overview(self):
        try:
            products = self.api_service.get_products()
            clients = self.api_service.get_clients()
            orders = self.api_service.get_orders()
            inventory = self.api_service.get_inventory()
            batches = self.api_service.get_batches()
            suppliers = self.api_service.get_suppliers()
            
            low_stock = [i for i in inventory if i.get('quantity', 0) <= 10]
            
            text = f"""
<b>📦 Товары:</b>
  Всего товаров: {len(products)}
  Активных: {len([p for p in products if p.get('isActive', True)])}
  
<b>👥 Клиенты:</b>
  Всего клиентов: {len(clients)}
  
<b>🛒 Заказы:</b>
  Всего заказов: {len(orders)}
  В обработке: {len([o for o in orders if o.get('status') == 'В обработке'])}
  Выполнено: {len([o for o in orders if o.get('status') == 'Выполнен'])}
  Доставлено: {len([o for o in orders if o.get('status') == 'Доставлен'])}
  
<b>📋 Склад:</b>
  Всего позиций: {len(inventory)}
  Позиций с низким остатком (≤10): {len(low_stock)}
  Всего партий: {len(batches)}
  
<b>🚚 Поставщики:</b>
  Всего поставщиков: {len(suppliers)}
            """
            
            self.overview_text.setHtml(text)
        except Exception as e:
            self.overview_text.setHtml(f"<b style='color: red;'>Ошибка загрузки:</b> {e}")
    
    def create_orders_report_tab(self):
        """Вкладка отчета по заказам"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("🛒 Анализ заказов")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        period_label = QLabel("Период:")
        info_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["За все время", "Сегодня", "Эта неделя", "Этот месяц"])
        info_layout.addWidget(self.period_combo)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Номер", "Клиент", "Дата", "Сумма", "Статус"])
        layout.addWidget(self.orders_table)
        
        stats_label = QLabel("📊 Статистика заказов:")
        stats_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(stats_label)
        
        self.orders_stats = QTextEdit()
        self.orders_stats.setReadOnly(True)
        self.orders_stats.setMaximumHeight(120)
        layout.addWidget(self.orders_stats)
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        refresh_btn.clicked.connect(self.load_orders_report)
        btn_layout.addWidget(refresh_btn)
        
        export_label = QLabel("Экспорт:")
        btn_layout.addWidget(export_label)
        
        excel_btn = QPushButton("📊 Excel")
        excel_btn.setStyleSheet("background-color: #217346; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        excel_btn.clicked.connect(lambda: self.export_orders('excel'))
        btn_layout.addWidget(excel_btn)
        
        pdf_btn = QPushButton("📄 PDF")
        pdf_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        pdf_btn.clicked.connect(lambda: self.export_orders('pdf'))
        btn_layout.addWidget(pdf_btn)
        
        word_btn = QPushButton("📝 Word")
        word_btn.setStyleSheet("background-color: #2B579A; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        word_btn.clicked.connect(lambda: self.export_orders('word'))
        btn_layout.addWidget(word_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.load_orders_report()
        return widget
    
    def export_orders(self, fmt):
        """Экспорт отчета по заказам"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            orders = self.api_service.get_orders()
            data = []
            
            for order in orders:
                client_name = order.get('clientName') or ''
                if not client_name:
                    client = order.get('client', {})
                    client_name = client.get('fullName', '') if isinstance(client, dict) else str(client)
                if not client_name and order.get('clientId') is not None:
                    client_name = f"ID {order.get('clientId')}"
                
                date = order.get('orderDate', '')
                if date:
                    try:
                        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                        date = dt.strftime("%d.%m.%Y")
                    except:
                        pass
                
                try:
                    exp_amount = float(order.get('totalAmount') or 0)
                except (TypeError, ValueError):
                    exp_amount = 0.0
                data.append({
                    "Номер заказа": order.get('orderNumber', ''),
                    "Клиент": client_name,
                    "Дата": str(date),
                    "Сумма": f"{exp_amount:.2f}",
                    "Статус": order.get('status', '')
                })
            
            filters = {
                'excel': ("Excel Files (*.xlsx)", ".xlsx"),
                'pdf': ("PDF Files (*.pdf)", ".pdf"),
                'word': ("Word Files (*.docx)", ".docx")
            }
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить отчет",
                f"orders_report_{datetime.now().strftime('%Y%m%d')}",
                filters[fmt][0]
            )
            
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
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Ошибка", "Не удалось сохранить отчет")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", f"Ошибка экспорта: {e}")
    
    def load_orders_report(self):
        try:
            orders = self.api_service.get_orders()
            
            self.orders_table.setRowCount(len(orders))
            total = 0
            statuses = {}
            
            for i, order in enumerate(orders[:100]):
                self.orders_table.setItem(i, 0, QTableWidgetItem(str(order.get('orderNumber', ''))))
                
                client_name = order.get('clientName') or ''
                if not client_name:
                    client = order.get('client', {})
                    client_name = client.get('fullName', '') if isinstance(client, dict) else str(client)
                if not client_name:
                    client_name = f"ID {order.get('clientId')}" if order.get('clientId') is not None else 'Неизвестен'
                self.orders_table.setItem(i, 1, QTableWidgetItem(client_name))
                
                date = order.get('orderDate', '')
                if date:
                    try:
                        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                        date = dt.strftime("%d.%m.%Y")
                    except:
                        pass
                self.orders_table.setItem(i, 2, QTableWidgetItem(str(date)))
                
                try:
                    amount = float(order.get('totalAmount') or 0)
                except (TypeError, ValueError):
                    amount = 0.0
                total += amount
                self.orders_table.setItem(i, 3, QTableWidgetItem(f"₽{amount:,.2f}"))
                
                status = order.get('status', 'Неизвестен')
                self.orders_table.setItem(i, 4, QTableWidgetItem(status))
                
                statuses[status] = statuses.get(status, 0) + 1
            
            status_text = "<br>".join([f"{k}: {v} шт." for k, v in statuses.items()])
            self.orders_stats.setHtml(f"""
<b>Всего заказов:</b> {len(orders)}<br>
<b>Общая сумма:</b> ₽{total:,.2f}<br>
<b>Средний чек:</b> ₽{(total/len(orders) if orders else 0):,.2f}<br>
<br><b>По статусам:</b><br>{status_text}
            """)
        except Exception as e:
            self.orders_stats.setHtml(f"<b style='color: red;'>Ошибка:</b> {e}")
    
    def create_inventory_report_tab(self):
        """Вкладка отчета по складу"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("📋 Состояние склада")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "Товар", "Количество", "Место хранения", "Температура", "Статус"])
        layout.addWidget(self.inventory_table)
        
        stats_layout = QHBoxLayout()
        
        low_stock_label = QLabel("Низкий остаток (≤10):")
        self.low_stock_count = QLabel("0")
        stats_layout.addWidget(low_stock_label)
        stats_layout.addWidget(self.low_stock_count)
        
        stats_layout.addStretch()
        
        total_value_label = QLabel("Общая стоимость:")
        self.total_value = QLabel("₽0")
        stats_layout.addWidget(total_value_label)
        stats_layout.addWidget(self.total_value)
        
        layout.addLayout(stats_layout)
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        refresh_btn.clicked.connect(self.load_inventory_report)
        btn_layout.addWidget(refresh_btn)
        
        export_label = QLabel("Экспорт:")
        btn_layout.addWidget(export_label)
        
        excel_btn = QPushButton("📊 Excel")
        excel_btn.setStyleSheet("background-color: #217346; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        excel_btn.clicked.connect(lambda: self.export_inventory('excel'))
        btn_layout.addWidget(excel_btn)
        
        pdf_btn = QPushButton("📄 PDF")
        pdf_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        pdf_btn.clicked.connect(lambda: self.export_inventory('pdf'))
        btn_layout.addWidget(pdf_btn)
        
        word_btn = QPushButton("📝 Word")
        word_btn.setStyleSheet("background-color: #2B579A; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        word_btn.clicked.connect(lambda: self.export_inventory('word'))
        btn_layout.addWidget(word_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.load_inventory_report()
        return widget
    
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
                if quantity == 0:
                    status = "Нет"
                elif quantity <= 10:
                    status = "Мало"
                else:
                    status = "В наличии"
                
                data.append({
                    "ID": str(item.get('id', '')),
                    "Товар": product_map.get(item.get('productId'), 'Неизвестен'),
                    "Количество": str(quantity),
                    "Место хранения": item.get('storageLocation', '-'),
                    "Температура": item.get('storageTemperature', '-'),
                    "Статус": status
                })
            
            filters = {
                'excel': ("Excel Files (*.xlsx)", ".xlsx"),
                'pdf': ("PDF Files (*.pdf)", ".pdf"),
                'word': ("Word Files (*.docx)", ".docx")
            }
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить отчет",
                f"inventory_report_{datetime.now().strftime('%Y%m%d')}",
                filters[fmt][0]
            )
            
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
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Ошибка", "Не удалось сохранить отчет")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", f"Ошибка экспорта: {e}")
    
    def load_inventory_report(self):
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
            
            self.low_stock_count.setText(f"<b style='color: red;'>{low_stock}</b>")
            
            inventory_value = self.api_service.get_inventory_value()
            self.total_value.setText(f"<b style='color: green;'>₽{inventory_value:,.2f}</b>")
        except Exception as e:
            self.low_stock_count.setText(f"<b style='color: red;'>Ошибка</b>")
    
    def create_revenue_report_tab(self):
        """Вкладка отчета по выручке"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("💰 Финансовая статистика")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.revenue_text = QTextEdit()
        self.revenue_text.setReadOnly(True)
        layout.addWidget(self.revenue_text)
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        refresh_btn.clicked.connect(self.load_revenue_report)
        btn_layout.addWidget(refresh_btn)
        
        export_label = QLabel("Экспорт:")
        btn_layout.addWidget(export_label)
        
        excel_btn = QPushButton("📊 Excel")
        excel_btn.setStyleSheet("background-color: #217346; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        excel_btn.clicked.connect(lambda: self.export_revenue('excel'))
        btn_layout.addWidget(excel_btn)
        
        pdf_btn = QPushButton("📄 PDF")
        pdf_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        pdf_btn.clicked.connect(lambda: self.export_revenue('pdf'))
        btn_layout.addWidget(pdf_btn)
        
        word_btn = QPushButton("📝 Word")
        word_btn.setStyleSheet("background-color: #2B579A; color: white; padding: 8px 16px; border: none; border-radius: 4px;")
        word_btn.clicked.connect(lambda: self.export_revenue('word'))
        btn_layout.addWidget(word_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.load_revenue_report()
        return widget
    
    def export_revenue(self, fmt):
        """Экспорт финансового отчета"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            orders = self.api_service.get_orders()
            inventory_value = self.api_service.get_inventory_value()
            
            total_revenue = sum(float(o.get('totalAmount') or 0) for o in orders)
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
            
            filters = {
                'excel': ("Excel Files (*.xlsx)", ".xlsx"),
                'pdf': ("PDF Files (*.pdf)", ".pdf"),
                'word': ("Word Files (*.docx)", ".docx")
            }
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить отчет",
                f"revenue_report_{datetime.now().strftime('%Y%m%d')}",
                filters[fmt][0]
            )
            
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
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Ошибка", "Не удалось сохранить отчет")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", f"Ошибка экспорта: {e}")
    
    def load_revenue_report(self):
        try:
            orders = self.api_service.get_orders()
            inventory_value = self.api_service.get_inventory_value()
            
            total_revenue = sum(float(o.get('totalAmount') or 0) for o in orders)

            completed = sum(1 for o in orders if o.get('status') in ['Выполнен', 'Доставлен'])
            in_progress = sum(1 for o in orders if o.get('status') == 'В обработке')
            
            text = f"""
<b>💵 Выручка:</b><br>
  Общая выручка: <b style='color: green;'>₽{total_revenue:,.2f}</b><br>
  Средний чек: ₽{total_revenue/len(orders) if orders else 0:,.2f}<br>
<br>
<b>📊 Заказы:</b><br>
  Всего: {len(orders)}<br>
  Завершено: {completed}<br>
  В процессе: {in_progress}<br>
<br>
<b>📦 Стоимость склада:</b><br>
  Текущая стоимость: <b style='color: blue;'>₽{inventory_value:,.2f}</b><br>
            """
            
            self.revenue_text.setHtml(text)
        except Exception as e:
            self.revenue_text.setHtml(f"<b style='color: red;'>Ошибка:</b> {e}")


class DashboardWidget(QWidget):
    """Виджет панели управления"""
    
    # Сигнал обновления данных
    data_updated = pyqtSignal()

    # Сигналы быстрых действий (обрабатываются MainWindow: переход
    # на вкладку + открытие диалога создания)
    request_new_order = pyqtSignal()
    request_add_product = pyqtSignal()
    request_add_client = pyqtSignal()
    
    def __init__(self, api_service: ApiService):
        super().__init__()
        
        self.api_service = api_service
        self.config = Config()
        
        # Настройка логгера
        self.logger = logging.getLogger(__name__)
        
        # Таймер для автообновления
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        
        # Инициализация UI
        self.setup_ui()
        self.setup_styles()
        
        # Подключаем сигналы
        self.connect_signals()
        
        # Запускаем таймер автообновления (каждые 5 минут), но не активируем его сразу
        # self.refresh_timer.start(300000)  # Будет активирован после входа
        
        # НЕ загружаем начальные данные - будем грузить только после входа
        # self.refresh_data()  # Будет вызвано после авторизации
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Адаптивный заголовок
        title_label = QLabel("🌸 Панель управления")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Адаптивный Grid layout для карточек статистики
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)  # Уменьшаем отступы для адаптивности
        
        # Адаптивные карточки статистики с иконками для цветочного магазина
        self.products_count_card = self.create_stat_card("🌺 Товары", "0", "Всего товаров")
        self.active_products_card = self.create_stat_card("✅ Активные", "0", "Активные товары")
        self.clients_count_card = self.create_stat_card("👥 Клиенты", "0", "Всего клиентов")
        self.orders_count_card = self.create_stat_card("🛒 Заказы", "0", "Всего заказов")
        self.inventory_value_card = self.create_stat_card("📋 Склад", "₽0", "Стоимость склада")
        self.revenue_card = self.create_stat_card("💰 Выручка", "₽0", "Общая выручка")
        
        # Добавление карточек в адаптивный grid
        stats_grid.addWidget(self.products_count_card, 0, 0)
        stats_grid.addWidget(self.active_products_card, 0, 1)
        stats_grid.addWidget(self.clients_count_card, 0, 2)
        stats_grid.addWidget(self.orders_count_card, 1, 0)
        stats_grid.addWidget(self.inventory_value_card, 1, 1)
        stats_grid.addWidget(self.revenue_card, 1, 2)
        
        main_layout.addLayout(stats_grid)
        
        # Адаптивные кнопки быстрого доступа
        quick_actions_frame = QFrame()
        quick_actions_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        quick_actions_layout = QVBoxLayout(quick_actions_frame)
        
        quick_actions_title = QLabel("⚡ Быстрые действия")
        quick_actions_title.setFont(title_font)
        quick_actions_layout.addWidget(quick_actions_title)
        
        buttons_layout = QHBoxLayout()
        
        # Адаптивные кнопки действий с иконками
        self.new_order_btn = QPushButton("🛒 Новый заказ")
        self.new_order_btn.setMinimumWidth(120)
        self.new_order_btn.clicked.connect(self.create_new_order)
        
        self.add_product_btn = QPushButton("📦 Добавить товар")
        self.add_product_btn.setMinimumWidth(120)
        self.add_product_btn.clicked.connect(self.add_product)
        
        self.add_client_btn = QPushButton("👥 Добавить клиента")
        self.add_client_btn.setMinimumWidth(120)
        self.add_client_btn.clicked.connect(self.add_client)
        
        self.inventory_report_btn = QPushButton("📋 Отчет по складу")
        self.inventory_report_btn.setMinimumWidth(120)
        self.inventory_report_btn.clicked.connect(self.show_inventory_report)
        
        buttons_layout.addWidget(self.new_order_btn)
        buttons_layout.addWidget(self.add_product_btn)
        buttons_layout.addWidget(self.add_client_btn)
        buttons_layout.addWidget(self.inventory_report_btn)
        
        quick_actions_layout.addLayout(buttons_layout)
        main_layout.addWidget(quick_actions_frame)
        
        # Адаптивная информационная панель
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("ℹ️ Информация")
        info_title.setFont(title_font)
        info_layout.addWidget(info_title)
        
        self.last_update_label = QLabel("🔄 Последнее обновление: Загрузка...")
        self.status_label = QLabel("🟢 Статус: Подключено к API")
        
        info_layout.addWidget(self.last_update_label)
        info_layout.addWidget(self.status_label)
        
        main_layout.addWidget(info_frame)
        
        # Растягиваем пустое пространство
        main_layout.addStretch()
    
    def create_stat_card(self, title: str, value: str, subtitle: str) -> QFrame:
        """Создать адаптивную карточку статистики"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setMinimumSize(180, 100)  # Минимальный размер для адаптивности
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Значение
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Подзаголовок
        subtitle_label = QLabel(subtitle)
        subtitle_font = QFont()
        subtitle_font.setPointSize(8)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Сохраняем ссылку на label значения для обновления
        card.value_label = value_label
        
        return card
    
    def setup_styles(self):
        """Настройка стилей"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #c8e6c9;
            }
            
            QLabel {
                color: #333333;
            }
            
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                background-color: #4CAF50;
                color: #FFFFFF;
            }
            
            QPushButton:hover {
                background-color: #388E3C;
                color: #FFFFFF;
            }
            
            QPushButton:pressed {
                background-color: #1B5E20;
                color: #FFFFFF;
            }
        """)
    
    def connect_signals(self):
        """Подключение сигналов"""
        self.data_updated.connect(self.update_ui)
    
    def refresh_data(self):
        """Обновить данные"""
        try:
            # Проверяем, есть ли токен авторизации
            if not self.api_service.token:
                self.logger.info("Пропуск обновления данных - пользователь не авторизован")
                return
            
            # Получаем данные от API
            products = self.api_service.get_products()
            active_products = self.api_service.get_active_products()
            clients = self.api_service.get_clients()
            orders = self.api_service.get_orders()
            inventory_value = self.api_service.get_inventory_value()
            revenue = self.api_service.get_revenue()
            
            # Обновляем данные
            self.stats_data = {
                'products_count': len(products),
                'active_products_count': len(active_products),
                'clients_count': len(clients),
                'orders_count': len(orders),
                'inventory_value': inventory_value,
                'revenue': revenue
            }
            
            # Обновляем время последнего обновления
            from datetime import datetime
            self.last_update_time = datetime.now()
            
            # Отправляем сигнал обновления
            self.data_updated.emit()
            
            # Обновляем статус
            self.status_label.setText("Статус: Данные обновлены")
            
            self.logger.info("Данные панели управления успешно обновлены")
            
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении данных: {e}")
            self.status_label.setText(f"Статус: Ошибка - {e}")
    
    def update_ui(self):
        """Обновить интерфейс"""
        if hasattr(self, 'stats_data'):
            # Обновляем значения в карточках
            self.products_count_card.value_label.setText(str(self.stats_data['products_count']))
            self.active_products_card.value_label.setText(str(self.stats_data['active_products_count']))
            self.clients_count_card.value_label.setText(str(self.stats_data['clients_count']))
            self.orders_count_card.value_label.setText(str(self.stats_data['orders_count']))
            self.inventory_value_card.value_label.setText(f"₽{self.stats_data['inventory_value']:,.2f}")
            self.revenue_card.value_label.setText(f"₽{self.stats_data['revenue']:,.2f}")
            
            # Обновляем время последнего обновления
            if hasattr(self, 'last_update_time'):
                time_str = self.last_update_time.strftime("%d.%m.%Y %H:%M:%S")
                self.last_update_label.setText(f"Последнее обновление: {time_str}")
    
    def create_new_order(self):
        """Создать новый заказ (быстрое действие дашборда)"""
        self.request_new_order.emit()
    
    def add_product(self):
        """Добавить товар (быстрое действие дашборда)"""
        self.request_add_product.emit()
    
    def add_client(self):
        """Добавить клиента (быстрое действие дашборда)"""
        self.request_add_client.emit()
    
    def show_inventory_report(self):
        """Показать отчет по складу"""
        dialog = ReportsDialog(self.api_service, self)
        dialog.exec()
    
    def closeEvent(self, event):
        """Обработка закрытия виджета"""
        # Останавливаем таймер
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        event.accept()