#!/bin/bash

# Скрипт инициализации проекта Tor Proxy Server

echo "Инициализация проекта Tor Proxy Server..."

# Создание необходимых директорий
mkdir -p config/tor config/lyrebird config/caddy logs

# Проверка наличия необходимых файлов
if [ ! -f .env ]; then
    echo "Создание .env файла из примера..."
    cp .env.example .env
    echo "Пожалуйста, настройте .env файл с вашими учетными данными"
fi

# Проверка наличия Dockerfile для каждого сервиса
if [ ! -f docker/tor/Dockerfile ]; then
    echo "ERROR: Dockerfile для Tor отсутствует!"
    exit 1
fi

if [ ! -f docker/lyrebird/Dockerfile ]; then
    echo "ERROR: Dockerfile для Lyrebird отсутствует!"
    exit 1
fi

if [ ! -f docker/api/Dockerfile ]; then
    echo "ERROR: Dockerfile для API отсутствует!"
    exit 1
fi

if [ ! -f docker/web/Dockerfile ]; then
    echo "ERROR: Dockerfile для Web UI отсутствует!"
    exit 1
fi

# Проверка наличия основных файлов
if [ ! -f docker-compose.yml ]; then
    echo "ERROR: docker-compose.yml отсутствует!"
    exit 1
fi

if [ ! -f README.md ]; then
    echo "ERROR: README.md отсутствует!"
    exit 1
fi

echo "Проект успешно инициализирован!"
echo ""
echo "Для запуска выполните:"
echo "1. Настройте .env файл: nano .env"
echo "2. Запустите проект: docker-compose up -d"
echo ""
echo "Доступ к веб-панели управления: https://wwcat.duckdns.org:8445/"