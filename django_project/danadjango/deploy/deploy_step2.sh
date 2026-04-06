#!/bin/bash

# Скрипт для установки Python зависимостей и настройки приложения

set -e

echo "=========================================="
echo "🔧 Установка зависимостей проекта"
echo "=========================================="

cd /var/www/qazaqdana

# Активация виртуального окружения и установка зависимостей
echo "📦 Установка Python пакетов..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Создание .env файла для продакшена
echo "⚙️ Создание .env файла..."
cat > .env << 'EOF'
SECRET_KEY=prod-django-insecure-qazaqdana-$(openssl rand -hex 32)
DEBUG=False
ALLOWED_HOSTS=109.248.32.73,qazaqdana.kz,www.qazaqdana.kz

# PostgreSQL Database
DB_NAME=qazaqdana_db
DB_USER=qazaqdana_user
DB_PASSWORD=QazaqDana2026!SecurePass
DB_HOST=localhost
DB_PORT=5432
EOF

# Создание директорий для статики и медиа
echo "📁 Создание директорий для статики..."
mkdir -p static media logs
chown -R qazaqdana:qazaqdana static media logs

# Применение миграций
echo "🗄️ Применение миграций..."
python manage.py makemigrations
python manage.py migrate

# Сбор статики
echo "🎨 Сбор статических файлов..."
python manage.py collectstatic --noinput

# Создание суперпользователя
echo "👤 Создание администратора..."
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@qazaqdana.kz', 'admin123')
    print("Суперпользователь создан: admin / admin123")
else:
    print("Суперпользователь уже существует")
PYEOF

# Инициализация данных
echo "📊 Инициализация данных..."
python manage.py init_data || echo "Данные уже инициализированы"
python manage.py init_ocr || echo "OCR данные уже инициализированы"

deactivate

echo "=========================================="
echo "✅ Установка зависимостей завершена"
echo "=========================================="
echo ""
echo "Следующий шаг: запустить deploy_step3.sh"
