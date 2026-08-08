# 💎 TK ALMAZ BOT

### Функционал

- Проверка пропуска на грузовом транспорте.
- Периодическая проверка пропусков в "гараже" и уведомление об изменениях.

### Настройка бота

1. Клонирование репозитория.
```bash
git clone https://github.com/gleb-gorokhov/tk-almaz-bot.git
cd tk-almaz-bot/
```

2. Запуск установщика.
```bash
chmod +x ./setup.sh
./setup.sh
```

3. Запуск бота.
```bash
source venv/bin/activate
python3 main.py
```

4. Настройка cron. Для примера: 12:00 по МСК.
```bash
crontab -e
0 9 * * * /home/tk-almaz-bot/venv/bin/python3 scheduled_report.py >> /home/cron_log.txt 2>&1
```

### Переменные окружения

- BOT_TOKEN
- API_KEY
