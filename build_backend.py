#!/usr/bin/env python3
"""
Скрипт для предварительной сборки бэкенда
Запускается перед основным start.py для предотвращения блокировки файлов
"""

import subprocess
import sys
from pathlib import Path

def build_backend():
    """Сборка бэкенда"""
    print("Предварительная сборка бэкенда...")
    
    project_root = Path(__file__).parent
    solution_path = project_root / "backend" / "App.sln"
    
    if solution_path.exists():
        # Сборка всего решения
        print(" Сборка всего решения...")
        result = subprocess.run([
            "dotnet", "build", str(solution_path), 
            "--configuration", "Debug"
        ], cwd=project_root, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f" Ошибка сборки: {result.stderr}")
            return False
        
        print(" Сборка завершена успешно")
        return True
    else:
        print(" Решение не найдено")
        return False

if __name__ == "__main__":
    success = build_backend()
    sys.exit(0 if success else 1)
