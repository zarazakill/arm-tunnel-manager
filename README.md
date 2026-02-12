# Tor Proxy Server для Raspberry Pi

Полнофункциональный прокси-сервер с поддержкой Tor, Bridges, Lyrebird и других транспортов на Raspberry Pi с веб-интерфейсом управления.

## Особенности

- Полностью автономная система в Docker-контейнерах
- Поддержка Tor, Bridges, Lyrebird, WebTunnel
- Веб-панель управления с авторизацией
- SOCKS5 и HTTP прокси для клиентов
- HTTPS доступ по адресу: https://wwcat.duckdns.org:8445/
- Поддержка мобильных устройств (Android/iOS)
- Подробное логирование и мониторинг

## Требования

- Raspberry Pi (любая модель с сетевым подключением)
- ОС: Raspbian/Debian/Raspberry Pi OS
- Docker и Docker Compose
- Внешний доступ к порту 8445

## Установка

### 1. Установка Docker на Raspberry Pi

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Добавляем текущего пользователя в группу docker
sudo usermod -aG docker $USER

# Устанавливаем Docker Compose (последняя версия)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагружаемся для применения изменений
sudo reboot
```

### 2. Настройка DuckDNS

1. Зарегистрируйтесь на [duckdns.org](https://www.duckdns.org/)
2. Создайте поддомен (например, `wwcat.duckdns.org`)
3. Установите клиент DuckDNS на ваш Raspberry Pi для автоматического обновления IP

### 3. Клонирование проекта

```bash
git clone https://github.com/yourusername/tor-proxy-server.git
cd tor-proxy-server
```

### 4. Настройка конфигурации

Создайте `.env` файл для настройки учетных данных:

```bash
cp .env.example .env
nano .env
```

Укажите:
- `ADMIN_USER=admin`
- `ADMIN_PASS=your_secure_password`
- `DUCKDNS_TOKEN=your_duckdns_token`

### 5. Запуск системы

```bash
docker-compose up -d
```

## Конфигурация домена

1. Убедитесь, что ваш поддомен DuckDNS (`wwcat.duckdns.org`) указывает на внешний IP вашего Raspberry Pi
2. Пробросьте порт 8445 на ваш Raspberry Pi в настройках роутера (Port Forwarding)
3. Проверьте доступность: `https://wwcat.duckdns.org:8445/`

## Использование

### Веб-панель управления

После запуска перейдите по адресу: `https://wwcat.duckdns.org:8445/`

Используйте учетные данные из `.env` файла для входа.

### Функции веб-панели

- **Статус сервисов**: Отображение состояния Tor, Lyrebird, Bridges
- **Текущий IP**: Показывает IP-адрес, который видят внешние сайты
- **Логи в реальном времени**: Просмотр логов всех компонентов
- **Управление**: Кнопки старт/стоп/рестарт/новая цепочка (NEWNYM)
- **Профили мостов**: Управление различными конфигурациями мостов

### Подключение клиентов

#### Android

1. Установите приложение Orbot или Orfox
2. Или используйте настройки SOCKS5 прокси в браузере:
   - Адрес: `wwcat.duckdns.org`
   - Порт: `8445`
   - Тип: SOCKS5

#### iOS

1. Используйте настройки прокси в Safari:
   - Настройки → Wi-Fi → Настроить прокси → Ручная
   - Адрес: `wwcat.duckdns.org`
   - Порт: `8445`
   - Тип: SOCKS

#### Компьютер (Windows/Mac/Linux)

Настройте SOCKS5 прокси в браузере или системе:
- Адрес: `wwcat.duckdns.org`
- Порт: `8445`
- Тип: SOCKS5

## Управление через API

Система предоставляет REST API для программного управления:

- `GET /api/status` - Получить статус сервисов
- `POST /api/start` - Запустить Tor
- `POST /api/stop` - Остановить Tor
- `POST /api/restart` - Перезапустить Tor
- `POST /api/newnym` - Запросить новую цепочку (NEWNYM)
- `GET /api/logs` - Получить логи

## Мониторинг и логирование

Все логи хранятся в директории `/var/log/tor-proxy/` внутри контейнеров:
- `tor.log` - Логи Tor
- `lyrebird.log` - Логи Lyrebird
- `api.log` - Логи API сервера
- `webui.log` - Логи веб-интерфейса

Логи также доступны через веб-панель в разделе "Логи".

## Безопасность

- Веб-панель защищена логином/паролем
- Все API эндпоинты требуют аутентификации
- Контейнеры работают с минимальными привилегиями
- HTTPS шифрование для всего трафика
- Рекомендуется использовать SSL-сертификаты (LetsEncrypt)

## Добавление мостов

Для настройки мостов:

1. Войдите в веб-панель
2. Перейдите в раздел "Мосты"
3. Добавьте конфигурацию моста в формате Tor:
   ```
   Bridge obfs4 IP:PORT CERT FINGERPRINT
   ```
4. Сохраните и перезапустите Tor

## Обновление проекта

```bash
# Остановите текущие контейнеры
docker-compose down

# Обновите код
git pull origin main

# Соберите новые образы
docker-compose build

# Запустите обновленную систему
docker-compose up -d
```

## Устранение неполадок

### Проверка статуса контейнеров

```bash
docker-compose ps
```

### Просмотр логов

```bash
docker-compose logs -f
```

### Проверка работы Tor

```bash
curl --socks5-hostname localhost:9050 https://check.torproject.org/api/ip
```

### Проблемы с доступом извне

- Убедитесь, что порт 8445 открыт на вашем роутере
- Проверьте, что DuckDNS правильно обновляет IP
- Проверьте настройки фаервола на Raspberry Pi

## Архитектура

Проект состоит из следующих компонентов:

- **tor-container**: Запускает Tor с мостами и плагинами
- **lyrebird-container**: Обеспечивает транспорт Lyrebird
- **api-server**: Управление сервисами через API
- **web-ui**: Веб-интерфейс для управления
- **reverse-proxy**: Обработка HTTPS и маршрутизации

## Лицензия

MIT License. См. файл LICENSE для подробностей.