#!/bin/bash

# Скрипт для настройки Gunicorn, Nginx и Supervisor

set -e

echo "=========================================="
echo "🌐 Настройка веб-сервера"
echo "=========================================="

# Создание systemd сервиса для Gunicorn
echo "⚙️ Создание Gunicorn сервиса..."
cat > /etc/systemd/system/meta-university.service << 'EOF'
[Unit]
Description=Qazaq Dana Django Application
After=network.target

[Service]
Type=notify
User=meta-university
Group=www-data
WorkingDirectory=/var/www/meta-university
Environment="PATH=/var/www/meta-university/venv/bin"
ExecStart=/var/www/meta-university/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/meta-university/gunicorn.sock \
    --timeout 120 \
    --access-logfile /var/www/meta-university/logs/gunicorn-access.log \
    --error-logfile /var/www/meta-university/logs/gunicorn-error.log \
    danadjango.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Настройка Nginx
echo "🌐 Настройка Nginx..."
cat > /etc/nginx/sites-available/meta-university << 'EOF'
server {
    listen 80;
    server_name 109.248.32.73 meta-university.kz www.meta-university.kz;

    client_max_body_size 50M;

    access_log /var/www/meta-university/logs/nginx-access.log;
    error_log /var/www/meta-university/logs/nginx-error.log;

    location /static/ {
        alias /var/www/meta-university/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/meta-university/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://unix:/var/www/meta-university/gunicorn.sock;
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
ln -sf /etc/nginx/sites-available/meta-university /etc/nginx/sites-enabled/
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
chown -R meta-university:www-data /var/www/meta-university
chmod -R 755 /var/www/meta-university
chmod -R 775 /var/www/meta-university/media
chmod -R 775 /var/www/meta-university/logs

# Запуск сервисов
echo "🚀 Запуск сервисов..."
systemctl daemon-reload
systemctl enable meta-university
systemctl start meta-university
systemctl restart nginx

echo "=========================================="
echo "✅ Деплой завершен успешно!"
echo "=========================================="
echo ""
echo "🎉 Приложение доступно по адресу: http://109.248.32.73"
echo ""
echo "📋 Полезные команды:"
echo "  - Перезапуск приложения: sudo systemctl restart meta-university"
echo "  - Логи приложения: sudo journalctl -u meta-university -f"
echo "  - Логи Gunicorn: tail -f /var/www/meta-university/logs/gunicorn-error.log"
echo "  - Логи Nginx: tail -f /var/www/meta-university/logs/nginx-error.log"
echo "  - Статус сервиса: sudo systemctl status meta-university"
echo ""
echo "🔐 Учетные данные администратора:"
echo "  URL: http://109.248.32.73/login/"
echo "  Логин: admin"
echo "  Пароль: admin123"
