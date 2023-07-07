import logging
import os
import sys
import time
from enum import Enum
from pathlib import Path

import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import RequestFailedException

BASE_DIR = Path(__file__).resolve().parent.parent

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


class Token(Enum):
    """Tokens."""

    PRACTICUM_TOKEN = 'PRACTICUM_TOKEN'
    TELEGRAM_TOKEN = 'TELEGRAM_TOKEN'
    TELEGRAM_CHAT_ID = 'TELEGRAM_CHAT_ID'


def check_tokens():
    """Checking the availability of environment variables."""
    for token in Token:
        if globals().get(token.value) is None:
            raise ValueError(f'Environment variable "{token.value}" not found')


def check_response(response: dict) -> list:
    """Checking response."""
    if not isinstance(response, dict):
        raise TypeError('Response does not contain a dict')

    if 'current_date' not in response:
        raise KeyError('The "current_date" key is not in the answer')

    if 'homeworks' not in response:
        raise KeyError('The "homeworks" key is not in the answer')

    if not isinstance(response['homeworks'], list):
        raise TypeError(
            'The "homeworks" key does not contain a list.',
            f' Response contein {type(response["homeworks"])}')

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
            raise RequestFailedException(
                f'API request failed:'
                f' {homework_statuses.status_code}'
            )
        homework = homework_statuses.json()
        return homework

    except requests.exceptions.RequestException as error:
        raise RequestFailedException from error(f'API request failed: {error}')


def parse_status(homework: dict) -> str:
    """Get status and retrurn verdict in str."""
    if 'homework_name' not in homework:
        logging.error('No homework_name in dict')
        raise KeyError('No homework name in dict')

    if 'status' not in homework:
        logging.error('No status in dict')
        raise KeyError('No status in dict')
    status = homework['status']

    if status not in HOMEWORK_VERDICTS:
        logging.error('Status is empty')
        raise KeyError('Status is empty or not in HOMEWORK_VERDICTS')

    verdict = HOMEWORK_VERDICTS[status]
    homework_name = homework['homework_name']

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Send message to Telegramm."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Telegram message has been sent')
    except Exception as error:
        logging.error(f'Bot failed to send message:"{message}", {error}')


def main():
    """The main logic of the bot."""
    try:
        check_tokens()
        last_message_sent = None
    except ValueError as error:
        logging.critical(f'Environment  variable {error} not found')
        sys.exit(1)
    bot = Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - RETRY_PERIOD
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            if not response['homeworks']:
                logging.debug('No new homework status.')
            else:
                for homework in response.get('homeworks'):
                    message = parse_status(homework)
                    if message != last_message_sent:
                        send_message(bot, message)
                        last_message_sent = message
            timestamp = response['current_date']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            response_type = type(
                response
            ).__name__ if 'response' in locals() else 'Unknown'
            logging.error(
                f'Main function faild: {error}\n',
                f' type of your response is: {response_type}'
            )
            if message != last_message_sent:
                send_message(bot, message)
                last_message_sent = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s'
        + ' - %(message)s - %(funcName)s - %(lineno)d',
        level=logging.DEBUG,
        filename=BASE_DIR / 'homework_bot' / 'main.log',
    )
    main()
