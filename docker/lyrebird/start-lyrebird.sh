#!/bin/bash

# Проверяем, существует ли файл конфигурации, если нет - создаем базовый
CONFIG_FILE="/etc/lyrebird/lyrebird.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default lyrebird configuration..."
    cat > "$CONFIG_FILE" << EOF
{
  "log": [
    {
      "filename": "/var/log/lyrebird/lyrebird.log",
      "level": "DEBUG"
    }
  ],
  "obfs4": {
    "enable": true,
    "port": 8443,
    "bindaddr": ":8443",
    "cert": "",
    "key": ""
  },
  "meeklite": {
    "enable": true,
    "port": 8080,
    "bindaddr": ":8080",
    "url": "",
    "front": "",
    "maxSessionPerIP": 10
  }
}
EOF
fi

# Запускаем lyrebird
echo "Starting Lyrebird..."
exec lyrebird -config "$CONFIG_FILE"