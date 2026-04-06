#!/bin/bash

# Скрипт для загрузки проекта на сервер через rsync

SERVER_IP="109.248.32.73"
SERVER_USER="root"
SERVER_PATH="/var/www/meta-university"
LOCAL_PATH="/Users/daniyarmukhtarov/Desktop/project/meta-university/danadjango"

echo "=========================================="
echo "📤 Загрузка проекта на сервер"
echo "=========================================="

# Создание директории на сервере
echo "📁 Создание директории на сервере..."
ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${SERVER_PATH}"

# Синхронизация файлов (исключая виртуальное окружение и кеш)
echo "🔄 Синхронизация файлов..."
rsync -avz --progress \
    --exclude='venv*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='db.sqlite3' \
    --exclude='media/*' \
    --exclude='static/CACHE' \
    --exclude='.env' \
    --exclude='*.log' \
    ${LOCAL_PATH}/ ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/

# Копирование production .env
echo "⚙️ Копирование production конфигурации..."
scp ${LOCAL_PATH}/deploy/.env.production ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/.env

echo "=========================================="
echo "✅ Файлы загружены на сервер"
echo "=========================================="
echo ""
echo "Теперь подключитесь к серверу и запустите:"
echo "  ssh ${SERVER_USER}@${SERVER_IP}"
echo "  cd ${SERVER_PATH}"
echo "  bash deploy/deploy_step2.sh"
