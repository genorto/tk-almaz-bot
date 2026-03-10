# 🚚 TK ALMAZ BOT

Телеграм-бот для ``ООО ТК «Алмаз»``

### Функционал

<ul>
    <li>Проверка пропусков по госномеру</li>
    <li>Хранение госномеров в "гараже"</li>
    <li>Отслеживание номеров и их периодическая проверка</li>
</ul>

### Настройка бота

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

### Переменные окружения

Требуется задать вручную в файле ``.env``
<ul>
    <li>BOT_TOKEN (Telegram @BotFather)</li>
    <li>PASSWORD</li>
    <li>API_KEY (https://parser-api.com/parser/transport_mos_api/?key=API_KEY)</li>
</ul>
