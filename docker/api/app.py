import os
import docker
import requests
import asyncio
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import subprocess
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tor Proxy API", description="API для управления Tor прокси сервером")

# Получение учетных данных из переменных окружения
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "your_secure_password")
TOR_CONTAINER_NAME = os.getenv("TOR_CONTAINER_NAME", "tor_proxy_tor")
LYREBRID_CONTAINER_NAME = os.getenv("LYREBRID_CONTAINER_NAME", "tor_proxy_lyrebird")

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Проверка учетных данных пользователя"""
    if credentials.username != ADMIN_USER or credentials.password != ADMIN_PASS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

class ServiceStatus(BaseModel):
    tor_status: str
    lyrebird_status: str
    current_ip: Optional[str]
    tor_version: Optional[str]
    bridges_enabled: bool

class CommandResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class BridgeConfig(BaseModel):
    bridge_line: str

# Инициализация Docker клиента
client = docker.from_env()

@app.get("/api/status", response_model=ServiceStatus)
async def get_status(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """Получить статус сервисов"""
    try:
        # Получаем статус контейнеров
        tor_container = None
        lyrebird_container = None
        
        try:
            tor_container = client.containers.get(TOR_CONTAINER_NAME)
            tor_status = tor_container.status
        except docker.errors.NotFound:
            tor_status = "not_found"
        
        try:
            lyrebird_container = client.containers.get(LYREBRID_CONTAINER_NAME)
            lyrebird_status = lyrebird_container.status
        except docker.errors.NotFound:
            lyrebird_status = "not_found"
        
        # Получаем текущий IP через Tor
        current_ip = None
        try:
            # Пробуем получить IP через Tor SOCKS5 прокси
            proxies = {
                'http': 'socks5://tor_proxy_tor:9050',
                'https': 'socks5://tor_proxy_tor:9050'
            }
            response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
            current_ip = response.json().get('origin')
        except Exception as e:
            logger.warning(f"Could not get current IP through Tor: {e}")
        
        # Проверяем версию Tor
        tor_version = None
        if tor_container and tor_container.status == "running":
            try:
                result = tor_container.exec_run("tor --version")
                tor_version = result.output.decode('utf-8').strip()
            except Exception as e:
                logger.error(f"Could not get Tor version: {e}")
        
        # Проверяем, включены ли мосты
        bridges_enabled = False
        if tor_container and tor_container.status == "running":
            try:
                result = tor_container.exec_run("cat /etc/tor/torrc")
                torrc_content = result.output.decode('utf-8')
                if "UseBridges 1" in torrc_content:
                    bridges_enabled = True
            except Exception as e:
                logger.error(f"Could not check bridge configuration: {e}")
        
        return ServiceStatus(
            tor_status=tor_status,
            lyrebird_status=lyrebird_status,
            current_ip=current_ip,
            tor_version=tor_version,
            bridges_enabled=bridges_enabled
        )
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/start", response_model=CommandResponse)
async def start_services(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """Запустить сервисы"""
    try:
        # Запускаем контейнеры если они остановлены
        try:
            tor_container = client.containers.get(TOR_CONTAINER_NAME)
            if tor_container.status != "running":
                tor_container.start()
                logger.info("Started Tor container")
        except docker.errors.NotFound:
            logger.error(f"Tor container {TOR_CONTAINER_NAME} not found")
            return CommandResponse(success=False, message=f"Tor container {TOR_CONTAINER_NAME} not found")
        
        try:
            lyrebird_container = client.containers.get(LYREBRID_CONTAINER_NAME)
            if lyrebird_container.status != "running":
                lyrebird_container.start()
                logger.info("Started Lyrebird container")
        except docker.errors.NotFound:
            logger.error(f"Lyrebird container {LYREBRID_CONTAINER_NAME} not found")
            return CommandResponse(success=False, message=f"Lyrebird container {LYREBRID_CONTAINER_NAME} not found")
        
        return CommandResponse(success=True, message="Services started successfully")
    except Exception as e:
        logger.error(f"Error starting services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stop", response_model=CommandResponse)
async def stop_services(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """Остановить сервисы"""
    try:
        # Останавливаем контейнеры
        try:
            tor_container = client.containers.get(TOR_CONTAINER_NAME)
            tor_container.stop()
            logger.info("Stopped Tor container")
        except docker.errors.NotFound:
            logger.error(f"Tor container {TOR_CONTAINER_NAME} not found")
            return CommandResponse(success=False, message=f"Tor container {TOR_CONTAINER_NAME} not found")
        
        try:
            lyrebird_container = client.containers.get(LYREBRID_CONTAINER_NAME)
            lyrebird_container.stop()
            logger.info("Stopped Lyrebird container")
        except docker.errors.NotFound:
            logger.error(f"Lyrebird container {LYREBRID_CONTAINER_NAME} not found")
            return CommandResponse(success=False, message=f"Lyrebird container {LYREBRID_CONTAINER_NAME} not found")
        
        return CommandResponse(success=True, message="Services stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/restart", response_model=CommandResponse)
async def restart_services(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """Перезапустить сервисы"""
    try:
        # Перезапускаем контейнеры
        try:
            tor_container = client.containers.get(TOR_CONTAINER_NAME)
            tor_container.restart()
            logger.info("Restarted Tor container")
        except docker.errors.NotFound:
            logger.error(f"Tor container {TOR_CONTAINER_NAME} not found")
            return CommandResponse(success=False, message=f"Tor container {TOR_CONTAINER_NAME} not found")
        
        try:
            lyrebird_container = client.containers.get(LYREBRID_CONTAINER_NAME)
            lyrebird_container.restart()
            logger.info("Restarted Lyrebird container")
        except docker.errors.NotFound:
            logger.error(f"Lyrebird container {LYREBRID_CONTAINER_NAME} not found")
            return CommandResponse(success=False, message=f"Lyrebird container {LYREBRID_CONTAINER_NAME} not found")
        
        return CommandResponse(success=True, message="Services restarted successfully")
    except Exception as e:
        logger.error(f"Error restarting services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/newnym", response_model=CommandResponse)
async def new_nym(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """Запросить новую цепочку (NEWNYM)"""
    try:
        # Отправляем сигнал NEWNYM в Tor
        tor_container = client.containers.get(TOR_CONTAINER_NAME)
        
        # Отправляем команду NEWNYM через Tor control port
        result = tor_container.exec_run(
            "printf 'AUTHENTICATE \"\"\r\nSIGNAL NEWNYM\r\n' | nc localhost 9051",
            workdir="/"
        )
        
        output = result.output.decode('utf-8')
        if "OK" in output:
            logger.info("Newnym signal sent successfully")
            return CommandResponse(success=True, message="Newnym signal sent successfully")
        else:
            logger.error(f"Failed to send newnym signal: {output}")
            return CommandResponse(success=False, message=f"Failed to send newnym signal: {output}")
    except Exception as e:
        logger.error(f"Error sending newnym signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/{service}")
async def get_logs(service: str, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """Получить логи сервиса"""
    try:
        if service == "tor":
            container = client.containers.get(TOR_CONTAINER_NAME)
            logs = container.logs(tail=100)
            return {"service": service, "logs": logs.decode('utf-8')}
        elif service == "lyrebird":
            container = client.containers.get(LYREBRID_CONTAINER_NAME)
            logs = container.logs(tail=100)
            return {"service": service, "logs": logs.decode('utf-8')}
        else:
            raise HTTPException(status_code=404, detail=f"Service {service} not found")
    except Exception as e:
        logger.error(f"Error getting logs for {service}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def get_all_logs(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """Получить логи всех сервисов"""
    try:
        logs = {}
        
        # Логи Tor
        try:
            tor_container = client.containers.get(TOR_CONTAINER_NAME)
            tor_logs = tor_container.logs(tail=50)
            logs["tor"] = tor_logs.decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting Tor logs: {e}")
            logs["tor"] = f"Error: {str(e)}"
        
        # Логи Lyrebird
        try:
            lyrebird_container = client.containers.get(LYREBRID_CONTAINER_NAME)
            lyrebird_logs = lyrebird_container.logs(tail=50)
            logs["lyrebird"] = lyrebird_logs.decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting Lyrebird logs: {e}")
            logs["lyrebird"] = f"Error: {str(e)}"
        
        return logs
    except Exception as e:
        logger.error(f"Error getting all logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bridges", response_model=CommandResponse)
async def add_bridge(bridge: BridgeConfig, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """Добавить мост в конфигурацию Tor"""
    try:
        # Получаем контейнер Tor
        tor_container = client.containers.get(TOR_CONTAINER_NAME)
        
        # Читаем текущий конфигурационный файл
        result = tor_container.exec_run("cat /etc/tor/torrc")
        current_config = result.output.decode('utf-8')
        
        # Проверяем, есть ли уже такой мост
        if bridge.bridge_line in current_config:
            return CommandResponse(success=False, message="Bridge already exists in configuration")
        
        # Добавляем строку моста в конфигурацию
        updated_config = current_config.strip() + f"\n{bridge.bridge_line}"
        
        # Записываем обновленный конфигурационный файл
        # Для этого нужно создать временный файл и скопировать его в контейнер
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(updated_config)
            temp_file_path = temp_file.name
        
        # Копируем файл в контейнер
        with open(temp_file_path, 'rb') as f:
            data = f.read()
        
        import io
        tar_stream = io.BytesIO()
        import tarfile
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            info = tarfile.TarInfo(name='torrc')
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        
        tar_stream.seek(0)
        tor_container.put_archive('/etc/tor/', tar_stream)
        
        # Удаляем временный файл
        os.unlink(temp_file_path)
        
        # Перезапускаем Tor для применения изменений
        tor_container.restart()
        
        logger.info(f"Added bridge: {bridge.bridge_line}")
        return CommandResponse(success=True, message="Bridge added successfully and Tor restarted")
    except Exception as e:
        logger.error(f"Error adding bridge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности API"""
    return {"message": "Tor Proxy API is running", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)