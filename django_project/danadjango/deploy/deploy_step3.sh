#!/bin/bash

# Скрипт для настройки Gunicorn, Nginx и Supervisor

set -e

echo "=========================================="
echo "🌐 Настройка веб-сервера"
echo "=========================================="

# Создание systemd сервиса для Gunicorn
echo "⚙️ Создание Gunicorn сервиса..."
cat > /etc/systemd/system/qazaqdana.service << 'EOF'
[Unit]
Description=Qazaq Dana Django Application
After=network.target

[Service]
Type=notify
User=qazaqdana
Group=www-data
WorkingDirectory=/var/www/qazaqdana
Environment="PATH=/var/www/qazaqdana/venv/bin"
ExecStart=/var/www/qazaqdana/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/qazaqdana/gunicorn.sock \
    --timeout 120 \
    --access-logfile /var/www/qazaqdana/logs/gunicorn-access.log \
    --error-logfile /var/www/qazaqdana/logs/gunicorn-error.log \
    danadjango.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Настройка Nginx
echo "🌐 Настройка Nginx..."
cat > /etc/nginx/sites-available/qazaqdana << 'EOF'
server {
    listen 80;
    server_name 109.248.32.73 qazaqdana.kz www.qazaqdana.kz;

    client_max_body_size 50M;

    access_log /var/www/qazaqdana/logs/nginx-access.log;
    error_log /var/www/qazaqdana/logs/nginx-error.log;

    location /static/ {
        alias /var/www/qazaqdana/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/qazaqdana/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://unix:/var/www/qazaqdana/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}
EOF

# Активация конфигурации Nginx
ln -sf /etc/nginx/sites-available/qazaqdana /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Тест конфигурации Nginx
echo "✅ Проверка конфигурации Nginx..."
nginx -t

# Настройка firewall
echo "🔥 Настройка firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# Установка прав доступа
echo "🔐 Установка прав доступа..."
chown -R qazaqdana:www-data /var/www/qazaqdana
chmod -R 755 /var/www/qazaqdana
chmod -R 775 /var/www/qazaqdana/media
chmod -R 775 /var/www/qazaqdana/logs

# Запуск сервисов
echo "🚀 Запуск сервисов..."
systemctl daemon-reload
systemctl enable qazaqdana
systemctl start qazaqdana
systemctl restart nginx

echo "=========================================="
echo "✅ Деплой завершен успешно!"
echo "=========================================="
echo ""
echo "🎉 Приложение доступно по адресу: http://109.248.32.73"
echo ""
echo "📋 Полезные команды:"
echo "  - Перезапуск приложения: sudo systemctl restart qazaqdana"
echo "  - Логи приложения: sudo journalctl -u qazaqdana -f"
echo "  - Логи Gunicorn: tail -f /var/www/qazaqdana/logs/gunicorn-error.log"
echo "  - Логи Nginx: tail -f /var/www/qazaqdana/logs/nginx-error.log"
echo "  - Статус сервиса: sudo systemctl status qazaqdana"
echo ""
echo "🔐 Учетные данные администратора:"
echo "  URL: http://109.248.32.73/login/"
echo "  Логин: admin"
echo "  Пароль: admin123"
