"""
Тема оформления для склада цветочного магазина
FloraStock - Система управления складом цветов
"""

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt

class FlowerWarehouseTheme:
    """Цветовая схема и стили для склада цветочного магазина"""
    
    # Основные цвета складской тематики с акцентом на цветы
    PRIMARY_GREEN = QColor(46, 125, 50)       # Основной зеленый (склад)
    SECONDARY_GREEN = QColor(27, 94, 32)     # Темно-зеленый
    LIGHT_GREEN = QColor(200, 230, 201)      # Светло-зеленый
    
    PRIMARY_BLUE = QColor(30, 136, 229)      # Основной синий (бизнес)
    SECONDARY_BLUE = QColor(25, 118, 210)    # Темно-синий
    LIGHT_BLUE = QColor(227, 242, 253)       # Светло-синий
    
    # Акцентные цвета для цветов
    FLOWER_PINK = QColor(233, 30, 99)        # Розовый (цветы)
    FLOWER_PURPLE = QColor(156, 39, 176)     # Фиолетовый (цветы)
    FLOWER_YELLOW = QColor(255, 193, 7)      # Желтый (цветы)
    FLOWER_ORANGE = QColor(255, 152, 0)      # Оранжевый (цветы)
    
    # Серые цвета для складской тематики
    WAREHOUSE_GRAY = QColor(96, 125, 139)    # Серый склада
    WHITE = QColor(255, 255, 255)             # Белый
    LIGHT_GRAY = QColor(245, 245, 245)       # Светло-серый
    MEDIUM_GRAY = QColor(158, 158, 158)      # Средне-серый
    DARK_GRAY = QColor(66, 66, 66)           # Темно-серый
    BLACK = QColor(33, 33, 33)               # Черный
    
    # Статусные цвета для склада
    SUCCESS_GREEN = QColor(76, 175, 80)      # Успех (завершено)
    WARNING_ORANGE = QColor(255, 152, 0)    # Предупреждение (в процессе)
    ERROR_RED = QColor(244, 67, 54)          # Ошибка (проблема)
    INFO_BLUE = QColor(33, 150, 243)         # Информация
    STORAGE_GRAY = QColor(158, 158, 158)     # Хранение (склад)
    
    @classmethod
    def get_palette(cls):
        """Получить цветовую палитру для складского приложения"""
        palette = QPalette()
        
        # Основные цвета
        palette.setColor(QPalette.ColorRole.Window, cls.WHITE)
        palette.setColor(QPalette.ColorRole.WindowText, cls.DARK_GRAY)
        palette.setColor(QPalette.ColorRole.Base, cls.WHITE)
        palette.setColor(QPalette.ColorRole.AlternateBase, cls.LIGHT_GRAY)
        palette.setColor(QPalette.ColorRole.Text, cls.DARK_GRAY)
        
        # Кнопки (складская тематика)
        palette.setColor(QPalette.ColorRole.Button, cls.PRIMARY_GREEN)
        palette.setColor(QPalette.ColorRole.ButtonText, cls.WHITE)
        palette.setColor(QPalette.ColorRole.Highlight, cls.LIGHT_BLUE)
        palette.setColor(QPalette.ColorRole.HighlightedText, cls.DARK_GRAY)
        
        return palette
    
    @classmethod
    def get_font(cls, size=10, bold=False):
        """Получить шрифт для приложения"""
        font = QFont("Segoe UI", size)
        font.setBold(bold)
        return font
    
    @classmethod
    def get_header_font(cls):
        """Шрифт для заголовков"""
        return cls.get_font(14, bold=True)
    
    @classmethod
    def get_button_style(cls, color_type="primary"):
        """Стиль для кнопок складской тематики"""
        styles = {
            "primary": f"""
                QPushButton {{
                    background-color: {cls.PRIMARY_GREEN.name()};
                    color: #FFFFFF;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {cls.SECONDARY_GREEN.name()};
                    color: #FFFFFF;
                }}
                QPushButton:pressed {{
                    background-color: #1B5E20;
                    color: #FFFFFF;
                }}
                QPushButton:disabled {{
                    background-color: {cls.MEDIUM_GRAY.name()};
                    color: #999999;
                }}
            """,
            "secondary": f"""
                QPushButton {{
                    background-color: {cls.WAREHOUSE_GRAY.name()};
                    color: #FFFFFF;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {cls.DARK_GRAY.name()};
                    color: #FFFFFF;
                }}
            """,
            "accent": f"""
                QPushButton {{
                    background-color: {cls.FLOWER_PINK.name()};
                    color: #FFFFFF;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {cls.FLOWER_PURPLE.name()};
                    color: #FFFFFF;
                }}
            """,
            "warehouse": f"""
                QPushButton {{
                    background-color: {cls.PRIMARY_BLUE.name()};
                    color: #FFFFFF;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {cls.SECONDARY_BLUE.name()};
                    color: #FFFFFF;
                }}
            """
        }
        return styles.get(color_type, styles["primary"])
    
    @classmethod
    def get_toolbar_button_style(cls):
        """Стиль для кнопок тулбара с хорошей видимостью"""
        return f"""
            QPushButton {{
                background-color: #2196F3;
                color: #000000;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
                color: #000000;
            }}
            QPushButton:pressed {{
                background-color: #0D47A1;
                color: #FFFFFF;
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
                color: #757575;
            }}
        """
    
    @classmethod
    def get_action_button_style(cls):
        """Стиль для кнопок действий в таблицах"""
        return f"""
            QPushButton {{
                background-color: #607D8B;
                color: #FFFFFF;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                min-width: 24px;
                min-height: 24px;
            }}
            QPushButton:hover {{
                background-color: #455A64;
                color: #FFFFFF;
            }}
        """
    
    @classmethod
    def get_table_style(cls):
        """Стиль для таблиц склада"""
        return f"""
            QTableWidget {{
                background-color: white;
                alternate-background-color: {cls.LIGHT_GRAY.name()};
                gridline-color: {cls.MEDIUM_GRAY.name()};
                border: 1px solid {cls.WAREHOUSE_GRAY.name()};
                border-radius: 6px;
                selection-background-color: {cls.LIGHT_BLUE.name()};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {cls.LIGHT_GRAY.name()};
            }}
            QTableWidget::item:selected {{
                background-color: {cls.LIGHT_BLUE.name()};
                color: {cls.DARK_GRAY.name()};
            }}
            QHeaderView::section {{
                background-color: {cls.PRIMARY_GREEN.name()};
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
        """
    
    @classmethod
    def get_status_style(cls, status):
        """Стиль для статусов склада"""
        status_colors = {
            # Статусы заказов
            "Новый": cls.PRIMARY_GREEN,
            "В обработке": cls.WARNING_ORANGE,
            "Готов к выдаче": cls.FLOWER_PURPLE,
            "Выполнен": cls.SUCCESS_GREEN,
            "Отменен": cls.ERROR_RED,
            
            # Статусы клиентов
            "Активен": cls.SUCCESS_GREEN,
            "Неактивен": cls.STORAGE_GRAY,
            
            # Статусы склада
            "В наличии": cls.SUCCESS_GREEN,
            "Заканчивается": cls.WARNING_ORANGE,
            "Нет в наличии": cls.ERROR_RED,
            "В пути": cls.INFO_BLUE,
            "На складе": cls.PRIMARY_GREEN,
            
            # Приоритеты
            "low": cls.SUCCESS_GREEN,
            "medium": cls.WARNING_ORANGE,
            "high": cls.ERROR_RED,
            
            # Статусы партий
            "Свежие": cls.FLOWER_PINK,
            "Нормальные": cls.SUCCESS_GREEN,
            "Старые": cls.WARNING_ORANGE,
            "Просроченные": cls.ERROR_RED
        }
        
        color = status_colors.get(status, cls.STORAGE_GRAY)
        return f"""
            QLabel {{
                background-color: {color.name()};
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 11px;
            }}
        """

# Название приложения
APP_NAME = "🌸 FloraStock"
APP_SUBTITLE = "Система управления складом цветов"
