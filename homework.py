import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filename='main.log',
)

#############################################


def check_tokens():
    """Checking the availability of environment variables."""
    required_env_vars = [
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ]
    for env_var in required_env_vars:
        if env_var is None:
            logging.critical(f'Environment  variable "{env_var}" not found')
            raise ValueError(f'Environment  variable "{env_var}" not found')
    return True


def check_response(response: dict) -> list:
    """Checking response."""
    if not isinstance(response, dict):
        logging.error('Response is not a dictionary')
        raise TypeError('Response does not contain a dict')

    if 'homeworks' not in response:
        logging.error('The "homeworks" key is not in the answer')
        raise KeyError('The "homeworks" key is not in the answer')

    if not isinstance(response['homeworks'], list):
        logging.error('Response is not a list')
        raise TypeError('The "homeworks" key does not contain a list')

    return response


def get_api_answer(timestamp):
    """Return answer API."""
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params={
                'from_date': timestamp
            }
        )
        if homework_statuses.status_code != 200:
            raise Exception(
                f'API request failed:'
                f' {homework_statuses.status_code}'
            )
        homework = homework_statuses.json()
        return homework

    except requests.exceptions.RequestException as error:
        logging.error(f'API request failed: {error}')
        return None


def parse_status(homework: dict) -> str:
    """Get status and retrurn verdict in str."""
    if 'homework_name' not in homework:
        logging.error('No homework_name in dict')
        raise KeyError('No homework name in dict')

    status = homework['status']

    if status not in HOMEWORK_VERDICTS:
        logging.error('Status is empty')
        raise KeyError('Status is empty or not in HOMEWORK_VERDICTS')

    verdict = HOMEWORK_VERDICTS.get(status)
    homework_name = homework['homework_name']

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Send message to Telegramm."""
    if not TELEGRAM_CHAT_ID:
        raise ValueError('TELEGRAM_CHAT_ID environment variable is not set')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Telegram message has been sent')
    except Exception as error:
        logging.error(f'Bot failed to send message: {error}')


def main():
    """The main logic of the bot."""
    if not check_tokens():
        logging.critical('Environment  variable  not found')
        exit()
    else:
        while True:
            try:
                bot = Bot(token=TELEGRAM_TOKEN)
                timestamp = int(time.time())
                response = get_api_answer(timestamp)
                if check_response(response):
                    if len(response.get('homeworks')) == 0:
                        logging.debug('No new homework status.')
                    for homework in response.get('homeworks'):
                        message = parse_status(homework)
                        send_message(bot, message)
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logging.error(f'Main function faild: {error}')
            finally:
                time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
