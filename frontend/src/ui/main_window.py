"""
Главное окно приложения
"""

import sys
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QMessageBox,
    QStatusBar, QMenuBar, QSplitter, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon

from src.services.api_service import ApiService
from src.utils.config import Config
from src.ui.login_dialog import LoginDialog
from src.ui.widgets.products_widget import ProductsWidget
from src.ui.widgets.clients_widget import ClientsWidget
from src.ui.widgets.orders_widget import OrdersWidget
from src.ui.theme import FlowerWarehouseTheme, APP_NAME, APP_SUBTITLE
try:
    from src.ui.widgets.inventory_widget import InventoryWidget
except ImportError:
    # Если модуль не найден, создаем заглушку
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
    class InventoryWidget(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Модуль склада временно недоступен"))
    
    import logging
    logging.warning("Модуль inventory_widget не найден, используется заглушка")
from src.ui.widgets.dashboard_widget import DashboardWidget
from src.ui.widgets.employees_widget import EmployeesWidget
from src.ui.widgets.suppliers_widget import SuppliersWidget
from src.ui.widgets.batches_widget import BatchesWidget
from src.ui.widgets.reports_widget import ReportsWidget
from src.ui.widgets.categories_widget import CategoriesWidget
from src.ui.dialogs.database_connection_dialog import DatabaseConnectionDialog


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    # Сигналы
    user_logged_in = pyqtSignal(dict)
    user_logged_out = pyqtSignal()
    
    def __init__(self, api_service: ApiService, config: Config):
        super().__init__()
        
        self.api_service = api_service
        self.config = config
        self.current_user = None
        self.login_completed = False
        self.logger = logging.getLogger(__name__)
        self.hide()
        
        # Инициализация UI
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        # Подключение сигналов
        self.connect_signals()
        
        # Показываем диалог входа
        self.show_login()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle(f"{APP_NAME} - {APP_SUBTITLE}")
        self.setGeometry(100, 100, self.config.window_width, self.config.window_height)
        
        # Применяем тему склада
        self.setPalette(FlowerWarehouseTheme.get_palette())
        self.setFont(FlowerWarehouseTheme.get_font())
        self.setMinimumSize(800, 600)  # Минимальный размер для адаптивности
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout с адаптивными отступами
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Информационная панель пользователя с темой склада
        self.user_info_label = QLabel("Пользователь не авторизован")
        self.user_info_label.setStyleSheet(f"""
            QLabel {{
                background-color: {FlowerWarehouseTheme.LIGHT_BLUE.name()};
                color: {FlowerWarehouseTheme.DARK_GRAY.name()};
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-height: 20px;
                border: 1px solid {FlowerWarehouseTheme.PRIMARY_BLUE.name()};
            }}
        """)
        self.user_info_label.setWordWrap(True)  # Перенос длинного текста
        main_layout.addWidget(self.user_info_label)
        
        # Создание вкладок с адаптивными настройками
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)  # Разрешаем перемещение вкладок
        
        # Настройки для вкладок с темой склада
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {FlowerWarehouseTheme.WAREHOUSE_GRAY.name()};
                background: white;
                top: -1px;
                border-radius: 6px;
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar::tab {{
                background-color: {FlowerWarehouseTheme.LIGHT_GRAY.name()};
                color: {FlowerWarehouseTheme.DARK_GRAY.name()};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background-color: {FlowerWarehouseTheme.PRIMARY_GREEN.name()};
                color: white;
            }}
            QTabBar::tab:hover {{
                background-color: {FlowerWarehouseTheme.WAREHOUSE_GRAY.name()};
                color: white;
            }}
        """)
        
        # Создание виджетов для вкладок
        self.dashboard_widget = DashboardWidget(self.api_service)
        self.products_widget = ProductsWidget(self.api_service)
        self.clients_widget = ClientsWidget(self.api_service)
        self.orders_widget = OrdersWidget(self.api_service)
        self.inventory_widget = InventoryWidget(self.api_service)
        self.suppliers_widget = SuppliersWidget(self.api_service)
        self.batches_widget = BatchesWidget(self.api_service)
        self.reports_widget = ReportsWidget(self.api_service)
        self.categories_widget = CategoriesWidget(self.api_service)
        self.employees_widget = None  # Создается после авторизации для админов
        
        # Добавление вкладок с темой склада цветов
        self.tab_widget.addTab(self.dashboard_widget, "🏠 Дашборд")
        self.tab_widget.addTab(self.products_widget, "🌺 Товары")
        self.tab_widget.addTab(self.categories_widget, "📁 Категории")
        self.tab_widget.addTab(self.clients_widget, "👥 Клиенты")
        self.tab_widget.addTab(self.orders_widget, "🛒 Заказы")
        self.tab_widget.addTab(self.suppliers_widget, "🚚 Поставщики")
        self.tab_widget.addTab(self.batches_widget, "📦 Партии")
        self.tab_widget.addTab(self.reports_widget, "📊 Отчёты")
        self.tab_widget.addTab(self.inventory_widget, "📋 Склад")
        
        main_layout.addWidget(self.tab_widget)
        
        # Изначально скрываем вкладки до авторизации
        self.tab_widget.setEnabled(False)
    
    def setup_menu(self):
        """Настройка меню"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #f5f5f5;
                color: #000000;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #000000;
                padding: 4px 10px;
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
                color: #000000;
            }
            QMenu {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #000000;
            }
        """)
        
        # Меню Файл
        file_menu = menubar.addMenu("📁 Файл")
        
        # Подключение к БД
        db_action = QAction("🔌 Подключение к БД", self)
        db_action.triggered.connect(self.show_database_connection)
        file_menu.addAction(db_action)
        
        file_menu.addSeparator()
        
        # Выход
        exit_action = QAction("🚪 Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Пользователь
        self.user_menu = menubar.addMenu("Пользователь")
        
        # Профиль
        self.profile_action = QAction("Профиль", self)
        self.profile_action.triggered.connect(self.show_profile)
        self.user_menu.addAction(self.profile_action)
        
        # Сменить пароль
        self.change_password_action = QAction("Сменить пароль", self)
        self.change_password_action.triggered.connect(self.change_password)
        self.user_menu.addAction(self.change_password_action)
        
        # Разделитель
        self.user_menu.addSeparator()
        
        # Выход из системы
        self.logout_action = QAction("Выйти из системы", self)
        self.logout_action.triggered.connect(self.logout)
        self.user_menu.addAction(self.logout_action)
        
        # Изначально блокируем меню пользователя
        self.user_menu.setEnabled(False)
        
        # Меню Справка
        help_menu = menubar.addMenu("Справка")
        
        # О программе
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Настройка строки состояния"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Метка статуса
        self.status_label = QLabel("Готов")
        self.status_bar.addWidget(self.status_label)
        
        # Метка времени
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
        
        # Таймер для обновления времени
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # Обновляем каждую секунду
        
        self.update_time()
    
    def connect_signals(self):
        """Подключение сигналов"""
        self.user_logged_in.connect(self.on_user_logged_in)
        self.user_logged_out.connect(self.on_user_logged_out)
        # Быстрые действия дашборда: переход на вкладку + диалог создания
        self.dashboard_widget.request_new_order.connect(self.open_new_order_dialog)
        self.dashboard_widget.request_add_product.connect(self.open_add_product_dialog)
        self.dashboard_widget.request_add_client.connect(self.open_add_client_dialog)
    
    def open_new_order_dialog(self):
        """Быстрое действие: создать заказ с дашборда"""
        self.tab_widget.setCurrentWidget(self.orders_widget)
        self.orders_widget.add_order()
        self.dashboard_widget.refresh_data()
    
    def open_add_product_dialog(self):
        """Быстрое действие: добавить товар с дашборда"""
        self.tab_widget.setCurrentWidget(self.products_widget)
        self.products_widget.add_product()
        self.dashboard_widget.refresh_data()
    
    def open_add_client_dialog(self):
        """Быстрое действие: добавить клиента с дашборда"""
        self.tab_widget.setCurrentWidget(self.clients_widget)
        self.clients_widget.add_client()
        self.dashboard_widget.refresh_data()
    
    def show_login(self):
        """Показать диалог входа"""
        login_dialog = LoginDialog(self.api_service, self)
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_user = login_dialog.user_data
            self.login_completed = True
            self.user_logged_in.emit(self.current_user)
        else:
            if not self.login_completed:
                self.close()
    
    def on_user_logged_in(self, user_data):
        """Обработка входа пользователя"""
        self.current_user = user_data
        
        # Показываем главное окно после успешного входа
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Обновляем информацию о пользователе
        employee = user_data.get('employee', {})
        user_info = f"{employee.get('fullName', 'Неизвестный пользователь')} | "
        user_info += f"{employee.get('position', 'Должность не указана')}"
        self.user_info_label.setText(user_info)
        
        # Разблокируем вкладки и меню
        self.tab_widget.setEnabled(True)
        self.user_menu.setEnabled(True)
        
        # Проверяем уровень доступа и добавляем вкладку сотрудников для админов
        access_level = employee.get('accessLevel', '').lower()
        if access_level == 'admin':
            if self.employees_widget is None:
                self.employees_widget = EmployeesWidget(self.api_service)
            if self.tab_widget.indexOf(self.employees_widget) == -1:
                self.tab_widget.addTab(self.employees_widget, "👔 Сотрудники")
            self.employees_widget.refresh_data()
        
        # Проверяем, что токен установлен (без sleep — токен уже в api_service)
        if self.api_service.token:
            self.logger.info(f"Токен установлен: {self.api_service.token[:50]}...")
        else:
            self.logger.warning("Токен не установлен!")
            return
        
        # Обновляем данные во всех виджетах
        self.refresh_all_widgets()
        
        # Обновляем статус
        self.status_label.setText(f"Пользователь {employee.get('fullName')} вошел в систему")
        
        self.logger.info(f"Пользователь {employee.get('fullName')} вошел в систему")
    
    def on_user_logged_out(self):
        """Обработка выхода пользователя"""
        self.current_user = None
        
        # Останавливаем таймеры
        if hasattr(self.dashboard_widget, 'refresh_timer'):
            self.dashboard_widget.refresh_timer.stop()
        
        # Очищаем информацию о пользователе
        self.user_info_label.setText("Пользователь не авторизован")
        
        # Блокируем вкладки и меню
        self.tab_widget.setEnabled(False)
        self.user_menu.setEnabled(False)
        
        # Очищаем токен API
        self.api_service.clear_token()
        
        # Обновляем статус
        self.status_label.setText("Пользователь вышел из системы")
        
        self.logger.info("Пользователь вышел из системы")
        
        # Показываем диалог входа
        self.show_login()
    
    def logout(self):
        """Выход из системы"""
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите выйти из системы?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.hide()
            self.user_logged_out.emit()
            self.close()
    
    def show_database_connection(self):
        """Показать диалог подключения к БД"""
        dialog = DatabaseConnectionDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Применяем адрес API к работающему сервису (нужен повторный вход)
            new_url = dialog.get_api_url()
            if new_url != self.api_service.base_url:
                self.api_service.base_url = new_url
                self.api_service.clear_token()
                QMessageBox.information(
                    self, "Адрес API изменён",
                    f"Новый адрес: {new_url}\nВойдите заново.")
    
    def show_profile(self):
        """Показать профиль пользователя"""
        if not self.current_user:
            return
        
        employee = self.current_user.get('employee', {})
        profile_info = f"""
        <h3>Профиль пользователя</h3>
        <p><b>ФИО:</b> {employee.get('fullName', 'Не указано')}</p>
        <p><b>Должность:</b> {employee.get('position', 'Не указана')}</p>
        <p><b>Уровень доступа:</b> {employee.get('accessLevel', 'Не указан')}</p>
        <p><b>Email:</b> {employee.get('email', 'Не указан')}</p>
        <p><b>Телефон:</b> {employee.get('phoneNumber', 'Не указан')}</p>
        """
        
        QMessageBox.information(self, "Профиль", profile_info)
    
    def change_password(self):
        """Изменить пароль"""
        from .dialogs.change_password_dialog import ChangePasswordDialog
        
        dialog = ChangePasswordDialog(self.api_service, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Успех", "Пароль успешно изменен")
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = f"""
        <h2>🌸 {self.config.app_name}</h2>
        <p>Версия: {self.config.app_version}</p>
        <p>Система управления складом цветочного магазина</p>
        <p>© 2024 FloraStock</p>
        <p><b>Технологии:</b></p>
        <ul>
            <li>Backend: C# .NET 8.0</li>
            <li>Frontend: Python PyQt6</li>
            <li>Database: PostgreSQL</li>
        </ul>
        """
        
        QMessageBox.about(self, "О программе", about_text)
    
    def refresh_all_widgets(self):
        """Обновить данные во всех виджетах"""
        try:
            # Проверяем, что токен установлен
            if not self.api_service.token:
                self.logger.warning("Токен аутентификации не установлен, пропускаем обновление данных")
                return
            
            # Запускаем таймер автообновления для dashboard
            if hasattr(self.dashboard_widget, 'refresh_timer'):
                self.dashboard_widget.refresh_timer.start(300000)  # 5 минут
            
            # Обновляем данные во всех виджетах
            self.dashboard_widget.refresh_data()
            self.products_widget.refresh_data()
            self.categories_widget.refresh_data()
            self.clients_widget.refresh_data()
            self.orders_widget.refresh_data()
            self.suppliers_widget.refresh_data()
            self.batches_widget.refresh_data()
            self.reports_widget.refresh_data()
            self.inventory_widget.refresh_data()
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении данных: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось обновить данные: {e}")
    
    def update_time(self):
        """Обновить время в строке состояния"""
        from datetime import datetime
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.time_label.setText(current_time)
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        reply = QMessageBox.question(
            self, "Подтверждение выхода",
            "Вы уверены, что хотите выйти из приложения?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logger.info("Приложение закрыто")
            event.accept()
        else:
            event.ignore()