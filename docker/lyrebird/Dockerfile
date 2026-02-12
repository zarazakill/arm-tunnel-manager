FROM golang:1.19-alpine AS builder

# Установка зависимостей для сборки
RUN apk add --no-cache git build-base

# Клонируем репозиторий Lyrebird
RUN git clone https://gitlab.torproject.org/tpo/anti-censorship/pluggable-transports/lyrebird.git /go/src/lyrebird
WORKDIR /go/src/lyrebird

# Собираем lyrebird
RUN go build -o lyrebird .

FROM alpine:latest

# Установка необходимых пакетов
RUN apk --no-cache add ca-certificates

# Копируем исполняемый файл lyrebird из builder stage
COPY --from=builder /go/src/lyrebird/lyrebird /usr/local/bin/lyrebird

# Создание директорий для конфигов и логов
RUN mkdir -p /etc/lyrebird/ && mkdir -p /var/log/lyrebird/

# Копируем скрипт запуска
COPY docker/lyrebird/start-lyrebird.sh /usr/local/bin/start-lyrebird.sh
RUN chmod +x /usr/local/bin/start-lyrebird.sh

# Указываем точку входа
ENTRYPOINT ["/usr/local/bin/start-lyrebird.sh"]