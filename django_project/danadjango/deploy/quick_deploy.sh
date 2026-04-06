#!/bin/bash

# Быстрый деплой Qazaq Dana - всё в одной команде
# Использование: ./quick_deploy.sh

SERVER_IP="109.248.32.73"
SERVER_USER="root"
SERVER_PASS="zt7RM#q3;o70ZM"
PROJECT_PATH="/Users/daniyarmukhtarov/Desktop/project/qazaqdana/danadjango"

set -e

echo "=========================================="
echo "🚀 БЫСТРЫЙ ДЕПЛОЙ QAZAQ DANA"
echo "=========================================="
echo ""
echo "Сервер: ${SERVER_IP}"
echo "Путь проекта: ${PROJECT_PATH}"
echo ""

# Проверка наличия sshpass для автоматического ввода пароля
if ! command -v sshpass &> /dev/null; then
    echo "⚠️  sshpass не установлен"
    echo "Установите: brew install hudochenkov/sshpass/sshpass"
    echo "Или вводите пароль вручную при запросе: ${SERVER_PASS}"
fi

# Функция для выполнения команд на сервере
run_remote() {
    ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "$1"
}

# Шаг 1: Подготовка сервера
echo "📦 Шаг 1/5: Подготовка сервера..."
run_remote "apt-get update && apt-get install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx git curl supervisor ufw rsync"

# Шаг 2: Настройка PostgreSQL
echo "🗄️ Шаг 2/5: Настройка базы данных..."
run_remote "
sudo -u postgres psql -c \"CREATE DATABASE qazaqdana_db;\" 2>/dev/null || echo 'БД уже существует';
sudo -u postgres psql -c \"CREATE USER qazaqdana_user WITH PASSWORD 'QazaqDana2026!SecurePass';\" 2>/dev/null || echo 'Пользователь уже существует';
sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE qazaqdana_db TO qazaqdana_user;\";
"

# Шаг 3: Создание пользователя и директорий
echo "📁 Шаг 3/5: Создание структуры..."
run_remote "
useradd -m -s /bin/bash qazaqdana 2>/dev/null || echo 'Пользователь уже существует';
mkdir -p /var/www/qazaqdana;
chown qazaqdana:qazaqdana /var/www/qazaqdana;
"

# Шаг 4: Загрузка файлов проекта
echo "📤 Шаг 4/5: Загрузка проекта..."
cd ${PROJECT_PATH}
rsync -avz --progress \
    --exclude='venv*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='db.sqlite3' \
    --exclude='media/*' \
    --exclude='.DS_Store' \
    -e "ssh -o StrictHostKeyChecking=no" \
    ./ ${SERVER_USER}@${SERVER_IP}:/var/www/qazaqdana/

# Шаг 5: Запуск деплоя на сервере
echo "🔧 Шаг 5/5: Установка и настройка..."
run_remote "
cd /var/www/qazaqdana;
chmod +x deploy/*.sh;
bash deploy/deploy_step1.sh;
bash deploy/deploy_step2.sh;
bash deploy/deploy_step3.sh;
"

echo ""
echo "=========================================="
echo "✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
echo "=========================================="
echo ""
echo "🌐 Приложение доступно:"
echo "   http://${SERVER_IP}"
echo ""
echo "🔐 Данные для входа:"
echo "   Логин: admin"
echo "   Пароль: admin123"
echo ""
echo "📋 Полезные команды:"
echo "   Логи: ssh ${SERVER_USER}@${SERVER_IP} 'journalctl -u qazaqdana -f'"
echo "   Статус: ssh ${SERVER_USER}@${SERVER_IP} 'systemctl status qazaqdana'"
echo "   Перезапуск: ssh ${SERVER_USER}@${SERVER_IP} 'systemctl restart qazaqdana'"
echo ""
