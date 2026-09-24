#!/usr/bin/env python3
"""
Единый файл запуска проекта
Автоматически запускает бэкенд и фронтенд
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

class ProjectLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_process = None
        self.frontend_process = None
        
    def check_dependencies(self):
        """Проверка зависимостей"""
        print("Проверка зависимостей...")
        
        # Проверка .NET
        try:
            result = subprocess.run(['dotnet', '--version'], 
                                      capture_output=True, text=True)
            if result.returncode == 0:
                print(f" .NET: {result.stdout.strip()}")
            else:
                print(" .NET не найден. Установите .NET 8.0 SDK")
                return False
        except FileNotFoundError:
            print(" .NET не найден. Установите .NET 8.0 SDK")
            return False
        
        # Проверка Python
        print(f" Python: {sys.version}")
        
        # Проверка pip
        try:
            subprocess.run(['pip', '--version'], 
                         capture_output=True, check=True)
            print(" pip доступен")
        except subprocess.CalledProcessError:
            print(" pip не найден")
            return False
        
        return True
    
    def setup_database(self):
        """Настройка базы данных"""
        print("Настройка базы данных...")
        
        # Проверка PostgreSQL
        try:
            result = subprocess.run(['psql', '--version'], 
                                      capture_output=True, text=True)
            print(f" PostgreSQL: {result.stdout.split()[2]}")
        except FileNotFoundError:
            print(" PostgreSQL не найден. Убедитесь, что PostgreSQL установлен и запущен")
        
        # Создание базы данных (пропускаем, так как база Sclad уже существует)
        db_commands = [
            # "createdb Sclad",  # База данных уже существует
            # "psql -d Sclad -f docs/Sclad_Database_Init.sql"  # Таблицы уже созданы
        ]
        print(" База данных Sclad уже существует с таблицами")
        
        for cmd in db_commands:
            try:
                subprocess.run(cmd, shell=True, check=True, 
                             cwd=self.project_root)
                print(f" Выполнено: {cmd}")
            except subprocess.CalledProcessError as e:
                print(f" Ошибка при выполнении {cmd}: {e}")
    
    def install_dependencies(self):
        """Установка зависимостей"""
        print("Установка зависимостей...")
        
        # Установка Python зависимостей
        frontend_requirements = self.project_root / "frontend" / "requirements.txt"
        if frontend_requirements.exists():
            print("Установка Python зависимостей...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(frontend_requirements)
            ], check=True)
            print("Python зависимости установлены")
        
        # Восстановление .NET зависимостей
        backend_path = self.project_root / "backend"
        if (backend_path / "App.sln").exists():
            print("Восстановление .NET зависимостей...")
            subprocess.run([
                "dotnet", "restore", str(backend_path / "App.sln")
            ], check=True, cwd=backend_path)
            print(" .NET зависимости восстановлены")
    
    def start_backend(self):
        """Запуск бэкенда"""
        print("Запуск бэкенда...")
        
        backend_path = self.project_root / "backend" / "src" / "API"
        if not (backend_path / "API.csproj").exists():
            backend_path = self.project_root / "backend" / "src" / "FlowerShop.API"
        
        if (backend_path / "API.csproj").exists():
            # Запускаем бэкенд без сборки (сборка уже выполнена)
            self.backend_process = subprocess.Popen([
                "dotnet", "run", "--project", str(backend_path / "API.csproj"), "--no-build", "--no-restore"
            ], cwd=backend_path)
            
            print(" Бэкенд запущен на http://localhost:5000")
            print("Swagger UI: http://localhost:5000/swagger")
            return True
        else:
            print(" Проект бэкенда не найден")
            return False
    
    def start_frontend(self):
        """Запуск фронтенда"""
        print("Запуск фронтенда...")
        
        frontend_path = self.project_root / "frontend"
        main_script = frontend_path / "src" / "main.py"
        
        if main_script.exists():
            self.frontend_process = subprocess.Popen([
                sys.executable, str(main_script)
            ], cwd=frontend_path)
            
            print(" Фронтенд запущен")
            return True
        else:
            print(" Файл main.py не найден")
            return False
    
    def cleanup(self, signum=None, frame=None):
        """Очистка процессов при выходе"""
        print("\nОстановка процессов...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("Бэкенд остановлен")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("Фронтенд остановлен")
        
        print("До свидания!")
    
    def run(self):
        """Основной запуск"""
        print("Запуск проекта Системы Управления Бизнесом")
        print("=" * 50)
        
        # Регистрация обработчика сигналов
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        try:
            # Проверка зависимостей
            if not self.check_dependencies():
                print(" Необходимые зависимости не найдены")
                return 1
            
            # Установка зависимостей
            self.install_dependencies()
            
            # Предварительная сборка бэкенда
            print("Предварительная сборка бэкенда...")
            solution_path = self.project_root / "backend" / "App.sln"
            if solution_path.exists():
                print(" Сборка всего решения...")
                build_result = subprocess.run([
                    "dotnet", "build", str(solution_path), 
                    "--configuration", "Debug"
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if build_result.returncode != 0:
                    print(" Ошибка сборки бэкенда:")
                    print(" STDOUT:")
                    print(build_result.stdout)
                    print(" STDERR:")
                    print(build_result.stderr)
                    print(f" Код возврата: {build_result.returncode}")
                    return 1
                
                print(" Предварительная сборка завершена успешно")
            else:
                print(" Решение не найдено")
                return 1
            
            # Настройка базы данных
            self.setup_database()
            
            # Запуск бэкенда
            if not self.start_backend():
                return 1
            
            # Небольшая задержка для запуска бэкенда
            time.sleep(3)
            
            # Запуск фронтенда
            if not self.start_frontend():
                self.cleanup()
                return 1
            
            print("\n" + "=" * 50)
            print(" Проект успешно запущен!")
            print("Бэкенд: http://localhost:5000")
            print("API Документация: http://localhost:5000/swagger")
            print("Фронтенд: Desktop приложение")
            print("Нажмите Ctrl+C для остановки")
            print("=" * 50)
            
            # Ожидание завершения
            self.backend_process.wait()
            self.frontend_process.wait()
            
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f" Ошибка: {e}")
            return 1
        finally:
            self.cleanup()
        
        return 0


def main():
    """Точка входа"""
    launcher = ProjectLauncher()
    return launcher.run()


if __name__ == "__main__":
    sys.exit(main())