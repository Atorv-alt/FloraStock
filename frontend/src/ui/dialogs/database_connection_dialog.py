"""
Диалог подключения к базе данных
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFormLayout,
    QCheckBox
)
from PyQt6.QtCore import Qt


class DatabaseConnectionDialog(QDialog):
    """Диалог настройки подключения к PostgreSQL"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        self.config = config
        
        self.setup_ui()
        self.load_current_config()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("🌸 Подключение к базе данных")
        self.setFixedSize(480, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("🌺 Настройка подключения к PostgreSQL")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2e7d32;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel("Введите параметры подключения к базе данных")
        desc_label.setStyleSheet("color: #666; font-size: 12px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("http://localhost:5000/api")
        form_layout.addRow("🌐 API сервер:", self.api_url_input)
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("localhost")
        form_layout.addRow("🖥️ Хост:", self.host_input)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("5432")
        form_layout.addRow("🔌 Порт:", self.port_input)
        
        self.db_name_input = QLineEdit()
        self.db_name_input.setPlaceholderText("sclad")
        form_layout.addRow("🗄️ База данных:", self.db_name_input)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("postgres")
        form_layout.addRow("👤 Пользователь:", self.user_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("🔒 Пароль:", self.password_input)
        
        layout.addLayout(form_layout)
        
        self.auto_create_checkbox = QCheckBox("🔧 Автоматически создать базу данных, если её нет")
        self.auto_create_checkbox.setChecked(True)
        self.auto_create_checkbox.setStyleSheet("color: #666;")
        layout.addWidget(self.auto_create_checkbox)
        
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("🔍 Тест")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #8BC34A;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #689F38;
            }
        """)
        self.test_btn.clicked.connect(self.test_connection)
        
        self.create_btn = QPushButton("✨ Создать и подключить")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        self.create_btn.clicked.connect(self.create_and_connect)
        
        self.close_btn = QPushButton("❌ Закрыть")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                padding: 10px 20px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def load_current_config(self):
        """Загрузка текущей конфигурации"""
        self.api_url_input.setText(self.config.api_base_url)
        self.host_input.setText(self.config.db_host)
        self.port_input.setText(self.config.db_port)
        self.db_name_input.setText(self.config.db_name)
        self.user_input.setText(self.config.db_user)
        self.password_input.setText(self.config.db_password)
    
    def get_api_url(self) -> str:
        """Введённый адрес API без концевого слеша"""
        return self.api_url_input.text().strip().rstrip('/') or "http://localhost:5000/api"
    
    def _get_connection_params(self):
        """Получить параметры подключения"""
        return {
            'host': self.host_input.text().strip() or "localhost",
            'port': self.port_input.text().strip() or "5432",
            'dbname': self.db_name_input.text().strip() or "sclad",
            'user': self.user_input.text().strip() or "postgres",
            'password': self.password_input.text()
        }
    
    def test_connection(self):
        """Тестирование подключения к БД"""
        try:
            import psycopg2
            from psycopg2 import OperationalError
            
            params = self._get_connection_params()
            
            conn = psycopg2.connect(**params)
            conn.close()
            QMessageBox.information(self, "Успех", "✅ Подключение к базе данных успешно!")
        except ImportError:
            QMessageBox.warning(self, "Ошибка", 
                "Модуль psycopg2 не установлен.\n"
                "Установите: pip install psycopg2-binary")
        except OperationalError as e:
            error_msg = str(e)
            if "does not exist" in error_msg.lower():
                QMessageBox.warning(self, "База данных не найдена", 
                    f"База данных '{params['dbname']}' не существует.\n\n"
                    "Нажмите 'Создать и подключить' для автоматического создания.")
            else:
                QMessageBox.critical(self, "Ошибка", f"❌ Не удалось подключиться:\n{error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"❌ Ошибка:\n{str(e)}")
    
    def create_database(self):
        """Создание базы данных"""
        try:
            import psycopg2
            from psycopg2 import sql
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            params = self._get_connection_params()
            db_name = params.pop('dbname')
            
            conn = psycopg2.connect(**params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))
                cursor.close()
                conn.close()
                return True
            else:
                cursor.close()
                conn.close()
                return True
                
        except ImportError:
            QMessageBox.warning(self, "Ошибка", 
                "Модуль psycopg2 не установлен.\n"
                "Установите: pip install psycopg2-binary")
            return False
        except Exception as e:
            QMessageBox.critical(self, "Ошибка создания", f"❌ Не удалось создать базу данных:\n{str(e)}")
            return False
    
    def create_and_connect(self):
        """Создать БД и подключиться"""
        db_name = self.db_name_input.text().strip() or "sclad"
        
        try:
            import psycopg2
            from psycopg2 import sql
            
            params = self._get_connection_params()
            params_without_db = params.copy()
            params_without_db['dbname'] = 'postgres'
            
            conn = psycopg2.connect(**params_without_db)
            conn.set_isolation_level(0)
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))
                cursor.close()
                conn.close()
                
                self.config.save_db_config(
                    self.host_input.text().strip(),
                    self.port_input.text().strip() or "5432",
                    db_name,
                    self.user_input.text().strip(),
                    self.password_input.text(),
                    self.get_api_url()
                )
                
                QMessageBox.information(self, "Успех", 
                    f"✅ База данных '{db_name}' успешно создана!\n\n"
                    "Конфигурация сохранена. Перезапустите приложение.")
                self.accept()
            else:
                cursor.close()
                conn.close()
                
                self.config.save_db_config(
                    self.host_input.text().strip(),
                    self.port_input.text().strip() or "5432",
                    db_name,
                    self.user_input.text().strip(),
                    self.password_input.text(),
                    self.get_api_url()
                )
                
                QMessageBox.information(self, "Успех", 
                    f"✅ База данных '{db_name}' уже существует.\n\n"
                    "Конфигурация сохранена.")
                self.accept()
                
        except ImportError:
            QMessageBox.warning(self, "Ошибка", 
                "Модуль psycopg2 не установлен.\n"
                "Установите: pip install psycopg2-binary")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"❌ Не удалось создать базу данных:\n{str(e)}")