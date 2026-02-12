#!/bin/bash

# Проверяем, существует ли файл конфигурации, если нет - создаем базовый
CONFIG_FILE="/etc/tor/torrc"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default torrc configuration..."
    cat > "$CONFIG_FILE" << EOF
SocksPort 9050
SocksBindAddress 0.0.0.0
Log notice file /var/log/tor/tor.log
User debian-tor
DataDirectory /var/lib/tor
Nickname ${TOR_NICKNAME:-tor-proxy-server}
ORPort 9001
DirPort 9030
ExitPolicy reject *:*
ControlPort 9051
CookieAuthentication 0
HashedControlPassword 16:872860B7B3CC8975A4E18FA49764E286F882C4DDB8F8E76E3C471244F2

# Enable bridges
UseBridges 1

# Bridge configurations will be added here
# Bridge obfs4 IP:PORT CERT FINGERPRINT
EOF
fi

# Запускаем tor
echo "Starting Tor..."
exec tor -f "$CONFIG_FILE"