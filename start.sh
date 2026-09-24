#!/bin/bash
# Единый файл запуска проекта для Linux/macOS

echo "=========================================="
echo "Запуск проекта Системы Управления Бизнесом"
echo "=========================================="
echo

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 не найден. Установите Python 3.8+"
    exit 1
fi

# Проверка .NET
if ! command -v dotnet &> /dev/null; then
    echo ".NET не найден. Установите .NET 8.0 SDK"
    exit 1
fi

# Запуск Python скрипта
echo "Запуск проекта..."
python3 start.py

if [ $? -ne 0 ]; then
    echo
    echo "Ошибка при запуске проекта"
    exit 1
fi