FROM node:18-alpine

# Установка зависимостей
RUN apk add --no-cache python3 make g++

# Установка http-server для простого запуска веб-страниц
RUN npm install -g http-server

# Создание рабочей директории
WORKDIR /app

# Копирование файлов веб-интерфейса
COPY docker/web/index.html /app/index.html
COPY docker/web/style.css /app/style.css
COPY docker/web/script.js /app/script.js

# Создание директории для логов
RUN mkdir -p /app/logs

# Запуск веб-сервера
CMD ["http-server", "-p", "80", "-a", "0.0.0.0"]