@echo off
title Система Управления Бизнесом - Запуск
echo ==========================================
echo Запуск проекта Системы Управления Бизнесом
echo ==========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python не найден. Установите Python 3.8+
    pause
    exit /b 1
)

REM Проверка .NET
dotnet --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  .NET не найден. Установите .NET 8.0 SDK
    pause
    exit /b 1
)

REM Запуск Python скрипта
echo Запуск проекта...
python start.py

if %errorlevel% neq 0 (
    echo.
    echo  Ошибка при запуске проекта
    pause
)