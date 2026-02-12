FROM debian:bullseye-slim

# Установка необходимых пакетов
RUN apt-get update && apt-get install -y \
    tor \
    tor-geoipdb \
    obfs4proxy \
    python3 \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Создание директорий для конфигов и логов
RUN mkdir -p /etc/tor/ && mkdir -p /var/log/tor/

# Копируем скрипт запуска
COPY docker/tor/start-tor.sh /usr/local/bin/start-tor.sh
RUN chmod +x /usr/local/bin/start-tor.sh

# Указываем точку входа
ENTRYPOINT ["/usr/local/bin/start-tor.sh"]