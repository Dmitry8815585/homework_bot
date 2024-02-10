# Проект telegram bot
## Стек навыков проекта "homework_bot"
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Telegram API](https://img.shields.io/badge/Telegram_API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white) ![Logging](https://img.shields.io/badge/Logging-292929?style=for-the-badge&logo=logging&logoColor=white) ![API Requests](https://img.shields.io/badge/API_Requests-009688?style=for-the-badge&logo=requests&logoColor=white)


“homework_bot” это telegram-бот, который обращаться к API сервиса, узнает статус выполненной работы и отправляет уведомления, если он изменился.
 
 Также я реализовал логирование для бота. 
 
 Логируются следующие события:
 1.	Отсутствие обязательных переменных окружения во время запуска бота (уровень CRITICAL).
 2.	удачная отправка любого сообщения в Telegram (уровень DEBUG);
 3.	сбой при отправке сообщения в Telegram (уровень ERROR);
 4.	недоступность эндпоинта (уровень ERROR);
 5.	любые другие сбои при запросе к эндпоинту (уровень ERROR);
 6.	отсутствие ожидаемых ключей в ответе API (уровень ERROR);
 7.	неожиданный статус домашней работы, обнаруженный в ответе API (уровень ERROR);
 8.	отсутствие в ответе новых статусов (уровень DEBUG).
