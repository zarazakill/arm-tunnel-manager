FROM python:3.10-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
COPY docker/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Создание рабочей директории
WORKDIR /app

# Копирование исходного кода
COPY docker/api/app.py /app/app.py

# Создание директории для логов
RUN mkdir -p /app/logs

# Запуск приложения
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]