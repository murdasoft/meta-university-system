#!/bin/bash

# Простой деплой с пошаговым выполнением команд

echo "=========================================="
echo "🚀 ДЕПЛОЙ QAZAQ DANA - ПОШАГОВАЯ ИНСТРУКЦИЯ"
echo "=========================================="
echo ""
echo "IP сервера: 109.248.32.73"
echo "Пароль: zt7RM#q3;o70ZM"
echo ""

read -p "Нажмите Enter для подключения к серверу..."

# Подключение к серверу и выполнение команд
ssh root@109.248.32.73 << 'ENDSSH'

echo "=========================================="
echo "Шаг 1: Обновление системы"
echo "=========================================="
apt-get update
apt-get upgrade -y

echo ""
echo "=========================================="
echo "Шаг 2: Установка пакетов"
echo "=========================================="
apt-get install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx git curl supervisor ufw

echo ""
echo "=========================================="
echo "Шаг 3: Настройка PostgreSQL"
echo "=========================================="
sudo -u postgres psql << 'EOF'
CREATE DATABASE qazaqdana_db;
CREATE USER qazaqdana_user WITH PASSWORD 'QazaqDana2026!SecurePass';
ALTER ROLE qazaqdana_user SET client_encoding TO 'utf8';
ALTER ROLE qazaqdana_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE qazaqdana_user SET timezone TO 'Asia/Almaty';
GRANT ALL PRIVILEGES ON DATABASE qazaqdana_db TO qazaqdana_user;
\q
EOF

echo ""
echo "=========================================="
echo "Шаг 4: Создание пользователя и директорий"
echo "=========================================="
useradd -m -s /bin/bash qazaqdana || true
mkdir -p /var/www/qazaqdana
chown qazaqdana:qazaqdana /var/www/qazaqdana

echo ""
echo "=========================================="
echo "✅ Базовая настройка завершена!"
echo "=========================================="
echo ""
echo "Теперь загрузите файлы проекта с локального компьютера:"
echo ""
echo "На ВАШЕМ КОМПЬЮТЕРЕ выполните:"
echo "  cd /Users/daniyarmukhtarov/Desktop/project/qazaqdana/danadjango"
echo "  rsync -avz --exclude='venv*' --exclude='__pycache__' --exclude='.git' ./ root@109.248.32.73:/var/www/qazaqdana/"
echo ""
echo "После загрузки файлов вернитесь на сервер и запустите:"
echo "  cd /var/www/qazaqdana"
echo "  bash deploy/deploy_step2.sh"
echo "  bash deploy/deploy_step3.sh"

ENDSSH

echo ""
echo "Отключено от сервера."
