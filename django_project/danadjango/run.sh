#!/bin/bash

echo "🚀 Запуск Qazaqdana OCR Backend..."

# Активация виртуального окружения
source venv-danadjango/bin/activate

# Проверка PostgreSQL
echo "📊 Проверка PostgreSQL..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL не запущен. Запускаем..."
    brew services start postgresql@14
    sleep 2
fi

# Применение миграций
echo "🔄 Применение миграций..."
python manage.py makemigrations
python manage.py migrate

# Сборка статических файлов
echo "📦 Сборка статических файлов..."
python manage.py collectstatic --noinput

# Запуск сервера
echo "✅ Запуск сервера разработки..."
echo ""
echo "🌐 Сервер доступен по адресу: http://localhost:8000"
echo "🔐 Админ-панель: http://localhost:8000/admin/"
echo "📚 API документация: http://localhost:8000/swagger/"
echo ""
echo "Логин: admin"
echo "Пароль: admin123"
echo ""

python manage.py runserver
