# 🚚 TK ALMAZ BOT

![Python](https://img.shields.io/badge/Python-3.12.3-blue?style=for-the-badge&logo=python)

Телеграм-бот для ``ООО ТК «Алмаз»``

### 🚀 Функционал

<ul>
    <li>🔐 Аутентификация по паролю</li>
    <li>🔍 Проверка пропусков по госномеру</li>
</ul>

### 🛠️ Стек технологий</h3>

<ul>
    <li>python 3.12.3</li>
    <li>aiogram 3.4.1</li>
    <li>requests 2.31.0</li>
    <li>python-dotenv 1.0.0</li>
</ul>

### ⚙️ Настройка бота

1. Клонирование репозитория
```bash
git clone https://github.com/genorto/tk-almaz-bot.git
cd tk-almaz-bot/
```

2. Запуск установщика
```bash
chmod +x ./setup.sh
./setup.sh
```

3. Запуск бота
```bash
source venv/bin/activate
python3 main.py
```

### 🔡 Переменные окружения

Требуется задать вручную в файле ``.env``
<ul>
    <li>BOT_TOKEN (Telegram @BotFather)</li>
    <li>PASSWORD</li>
    <li>API_KEY (https://parser-api.com/parser/transport_mos_api/?key=API_KEY)</li>
</ul>

### 🏗️ Структура проекта

```
tk-almaz-bot/
├── app/
│   ├── config.py     # Конфигурация проекта
│   ├── handlers.py   # Обработчик сообщений
│   └── states.py     # Модель состояний FSM
├── service/
│   ├── api.py        # Обработка запросов к parser-api
│   ├── utils.py      # Вспомогательные функции
│   └── whitelist.py  # Работа с "белым списком"
├── .gitignore
├── main.py
├── README.md
├── requirements.txt
└── setup.sh
```
