#!/bin/bash

# Скрипт для автоматического деплоя Django проекта на Ubuntu 24.04
# Сервер: 109.248.32.73

set -e  # Остановка при ошибке

echo "=========================================="
echo "🚀 Начало деплоя Qazaq Dana"
echo "=========================================="

# Обновление системы
echo "📦 Обновление системы..."
apt-get update
apt-get upgrade -y

# Установка необходимых пакетов
echo "📦 Установка зависимостей..."
apt-get install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx git curl supervisor ufw

# Настройка PostgreSQL
echo "🗄️ Настройка PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE qazaqdana_db;" || echo "База данных уже существует"
sudo -u postgres psql -c "CREATE USER qazaqdana_user WITH PASSWORD 'QazaqDana2026!SecurePass';" || echo "Пользователь уже существует"
sudo -u postgres psql -c "ALTER ROLE qazaqdana_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE qazaqdana_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE qazaqdana_user SET timezone TO 'Asia/Almaty';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qazaqdana_db TO qazaqdana_user;"

# Создание пользователя для приложения
echo "👤 Создание пользователя приложения..."
useradd -m -s /bin/bash qazaqdana || echo "Пользователь уже существует"

# Создание директории проекта
echo "📁 Создание директорий..."
mkdir -p /var/www/qazaqdana
chown qazaqdana:qazaqdana /var/www/qazaqdana

# Клонирование или копирование проекта
echo "📥 Подготовка проекта..."
# В реальном случае здесь будет git clone или rsync
# Пока создадим структуру

# Создание виртуального окружения
echo "🐍 Создание виртуального окружения..."
cd /var/www/qazaqdana
python3.12 -m venv venv
chown -R qazaqdana:qazaqdana venv

echo "=========================================="
echo "✅ Базовая настройка завершена"
echo "=========================================="
echo ""
echo "Следующие шаги:"
echo "1. Загрузить файлы проекта в /var/www/qazaqdana/"
echo "2. Запустить deploy_step2.sh"
