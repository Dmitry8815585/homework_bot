## Проект telegram bot
# Стек: Python, Django, DRF, Telegramm
# “homework_bot” это telegram-бот, который обращаться к API сервису и узнает статус домашней работы: взята ли ваша работа в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку. Также я реализовал логирование для бота. Логируются следующие события:
# 1.	Отсутствие обязательных переменных окружения во время запуска бота (уровень CRITICAL).
# 2.	удачная отправка любого сообщения в Telegram (уровень DEBUG);
# 3.	сбой при отправке сообщения в Telegram (уровень ERROR);
# 4.	недоступность эндпоинта (уровень ERROR);
# 5.	любые другие сбои при запросе к эндпоинту (уровень ERROR);
# 6.	отсутствие ожидаемых ключей в ответе API (уровень ERROR);
# 7.	неожиданный статус домашней работы, обнаруженный в ответе API (уровень ERROR);
# 8.	отсутствие в ответе новых статусов (уровень DEBUG).
