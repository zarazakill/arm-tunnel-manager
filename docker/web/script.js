// Базовый URL API
const API_BASE_URL = '/api';

// Состояния сервисов
let currentStatus = {
    tor_status: 'unknown',
    lyrebird_status: 'unknown',
    current_ip: '-',
    bridges_enabled: false
};

// При загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация элементов DOM
    const torStatusEl = document.getElementById('tor-status');
    const lyrebirdStatusEl = document.getElementById('lyrebird-status');
    const currentIpEl = document.getElementById('current-ip');
    const bridgesStatusEl = document.getElementById('bridges-status');
    
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const restartBtn = document.getElementById('restart-btn');
    const newnymBtn = document.getElementById('newnym-btn');
    
    const logServiceSelect = document.getElementById('log-service');
    const refreshLogsBtn = document.getElementById('refresh-logs');
    const logsOutputEl = document.getElementById('logs-output');
    
    const bridgeInput = document.getElementById('bridge-input');
    const addBridgeBtn = document.getElementById('add-bridge-btn');
    const bridgeListEl = document.getElementById('bridge-list');
    
    // Установка обработчиков событий
    startBtn.addEventListener('click', startServices);
    stopBtn.addEventListener('click', stopServices);
    restartBtn.addEventListener('click', restartServices);
    newnymBtn.addEventListener('click', newNym);
    refreshLogsBtn.addEventListener('click', () => loadLogs(logServiceSelect.value));
    addBridgeBtn.addEventListener('click', addBridge);
    
    // Загрузка начального состояния
    loadStatus();
    
    // Обновление статуса каждые 10 секунд
    setInterval(loadStatus, 10000);
});

// Загрузка статуса сервисов
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/status`, {
            method: 'GET',
            headers: {
                'Authorization': 'Basic ' + btoa(getCredentials())
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentStatus = data;
        
        // Обновление отображения статуса
        updateStatusDisplay();
        
        // Загрузка логов
        loadLogs('all');
    } catch (error) {
        console.error('Error loading status:', error);
        showError('Ошибка загрузки статуса: ' + error.message);
    }
}

// Обновление отображения статуса
function updateStatusDisplay() {
    const torStatusEl = document.getElementById('tor-status');
    const lyrebirdStatusEl = document.getElementById('lyrebird-status');
    const currentIpEl = document.getElementById('current-ip');
    const bridgesStatusEl = document.getElementById('bridges-status');
    
    // Обновление статуса Tor
    torStatusEl.textContent = currentStatus.tor_status;
    torStatusEl.className = 'status-value';
    if (currentStatus.tor_status === 'running') {
        torStatusEl.classList.add('running');
    } else if (currentStatus.tor_status === 'exited') {
        torStatusEl.classList.add('stopped');
    } else {
        torStatusEl.classList.add('unknown');
    }
    
    // Обновление статуса Lyrebird
    lyrebirdStatusEl.textContent = currentStatus.lyrebird_status;
    lyrebirdStatusEl.className = 'status-value';
    if (currentStatus.lyrebird_status === 'running') {
        lyrebirdStatusEl.classList.add('running');
    } else if (currentStatus.lyrebird_status === 'exited') {
        lyrebirdStatusEl.classList.add('stopped');
    } else {
        lyrebirdStatusEl.classList.add('unknown');
    }
    
    // Обновление текущего IP
    currentIpEl.textContent = currentStatus.current_ip || '-';
    
    // Обновление статуса мостов
    bridgesStatusEl.textContent = currentStatus.bridges_enabled ? 'Включены' : 'Отключены';
    bridgesStatusEl.className = 'status-value';
    bridgesStatusEl.classList.add(currentStatus.bridges_enabled ? 'running' : 'stopped');
}

// Функция для получения учетных данных из localStorage или запроса
function getCredentials() {
    // Попробуем получить учетные данные из localStorage
    let username = localStorage.getItem('torProxyUsername');
    let password = localStorage.getItem('torProxyPassword');
    
    if (!username || !password) {
        // Если не найдены, запросим у пользователя
        username = prompt('Введите имя пользователя:');
        password = prompt('Введите пароль:');
        
        if (username && password) {
            localStorage.setItem('torProxyUsername', username);
            localStorage.setItem('torProxyPassword', password);
        }
    }
    
    return `${username}:${password}`;
}

// Функция для выполнения запросов с авторизацией
async function authenticatedFetch(url, options = {}) {
    const authOptions = {
        ...options,
        headers: {
            'Authorization': 'Basic ' + btoa(getCredentials()),
            ...options.headers
        }
    };
    
    return fetch(url, authOptions);
}

// Функции управления сервисами
async function startServices() {
    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/start`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showMessage(data.message);
        
        // Обновим статус после выполнения команды
        setTimeout(loadStatus, 2000);
    } catch (error) {
        console.error('Error starting services:', error);
        showError('Ошибка запуска сервисов: ' + error.message);
    }
}

async function stopServices() {
    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/stop`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showMessage(data.message);
        
        // Обновим статус после выполнения команды
        setTimeout(loadStatus, 2000);
    } catch (error) {
        console.error('Error stopping services:', error);
        showError('Ошибка остановки сервисов: ' + error.message);
    }
}

async function restartServices() {
    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/restart`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showMessage(data.message);
        
        // Обновим статус после выполнения команды
        setTimeout(loadStatus, 2000);
    } catch (error) {
        console.error('Error restarting services:', error);
        showError('Ошибка перезапуска сервисов: ' + error.message);
    }
}

async function newNym() {
    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/newnym`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showMessage(data.message);
        
        // Обновим статус после выполнения команды
        setTimeout(loadStatus, 2000);
    } catch (error) {
        console.error('Error sending newnym:', error);
        showError('Ошибка отправки NEWNYM: ' + error.message);
    }
}

// Загрузка логов
async function loadLogs(service = 'all') {
    try {
        let url;
        if (service === 'all') {
            url = `${API_BASE_URL}/logs`;
        } else {
            url = `${API_BASE_URL}/logs/${service}`;
        }
        
        const response = await authenticatedFetch(url, {
            method: 'GET'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const logsOutputEl = document.getElementById('logs-output');
        
        if (service === 'all') {
            // Форматируем все логи
            let logsText = '';
            for (const [serviceName, logs] of Object.entries(data)) {
                logsText += `=== ${serviceName.toUpperCase()} ===\n${logs}\n\n`;
            }
            logsOutputEl.textContent = logsText;
        } else {
            logsOutputEl.textContent = data.logs || data[service] || 'Нет логов';
        }
        
        // Прокрутка вниз
        logsOutputEl.scrollTop = logsOutputEl.scrollHeight;
    } catch (error) {
        console.error('Error loading logs:', error);
        showError('Ошибка загрузки логов: ' + error.message);
    }
}

// Добавление моста
async function addBridge() {
    const bridgeInput = document.getElementById('bridge-input');
    const bridgeLine = bridgeInput.value.trim();
    
    if (!bridgeLine) {
        showError('Введите конфигурацию моста');
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/bridges`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ bridge_line: bridgeLine })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showMessage(data.message);
        
        // Очистим поле ввода
        bridgeInput.value = '';
        
        // Обновим статус после добавления моста
        setTimeout(loadStatus, 2000);
    } catch (error) {
        console.error('Error adding bridge:', error);
        showError('Ошибка добавления моста: ' + error.message);
    }
}

// Вспомогательные функции для отображения сообщений
function showMessage(message) {
    alert(message);
}

function showError(message) {
    alert('Ошибка: ' + message);
}