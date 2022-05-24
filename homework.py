import logging
import os
import sys
import time
import requests
import telegram

from dotenv import load_dotenv
from http import HTTPStatus

import exceptions

logging.basicConfig(
    filename='main.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger.info('Бот запущен!')


def check_tokens() -> bool:
    """
    проверяет доступность переменных окружения, которые необходимы для
    работы программы. Если отсутствует хотя бы одна переменная окружения —
    функция должна вернуть False, иначе — True.
    """
    logger.info('Проверка переменных окружения')
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for token in tokens:
        if token is None:
            message = f'Нет переменной окружения - {token}!'
            logger.critical(message)
            return False
    return True


def send_message(bot, message):
    """ Отправляет сообщение в Telegram чат. """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Отправлено сообщение: "{message}"')
    except Exception as error:
        logger.error(f'Сообщение не отправлено: {error}')


def get_api_answer(current_timestamp):
    """ Делает запрос к единственному эндпоинту API-сервиса. """
    logger.info("Получение ответа от сервера")
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = HEADERS
    try:
        response = requests.get(ENDPOINT, headers=headers, params=params)
    except Exception:
        message = 'Нет ожидаемого ответа сервера от API'
        logger.error(message)
        raise exceptions.APIAnswerError(message)
    try:
        if response.status_code != HTTPStatus.OK:
            message = (f'Эндпоинт {ENDPOINT} не отвечает, ',
                       f'http status: {response.status_code}')
            logger.error(message)
            raise Exception(message)
    except Exception:
        message = 'Нет ожидаемого ответа сервера от API'
        logger.error(message)
        raise exceptions.APIAnswerError(message)
    return response.json()


def check_response(response):
    """ Проверяет ответ API на корректность. """
    logger.info("Проверка ответа API на корректность")
    if 'homeworks' not in response:
        raise TypeError('Ошибка: homeworks отсутствует')
    if len(response['homeworks']) == 0:
        raise IndexError('Ошибка: homeworks пуст')
    if not isinstance(response, dict):
        raise TypeError('Ошибка: ожидается словарь')
    if type(response['homeworks']) != list:
        raise TypeError('Ошибка: ожидался список')
    return response


def parse_status(homework):
    """
    Извлекает из информации о конкретной домашней работе статус этой
    работы.
    """
    logger.info(f'Парсим домашнее задание: {homework}')
    keys_homework = ['status', 'homework_name']
    for key in keys_homework:
        if key not in homework:
            message = f'ключ {keys_homework} отсутствует'
            raise KeyError(message)
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        message = 'неизвестный статус домашнего задания'
        raise KeyError(message)
    verdict = HOMEWORK_STATUSES[homework_status]
    logger.info('Получен статус')
    return f'Изменился статус проверки работы "{homework_name}" - {verdict}'


def checking_repeated_messages(message, last_response):
    """ Проверка и блок повторных сообщений. """
    logger.info('Проверка сообщения на повтор')
    if message != last_response:
        last_response = message
        logger.info('Cообщение не повторяется')
        return last_response
    else:
        logger.info('Cообщение повторяется')


def main():
    """ Основная логика работы бота. """
    if not check_tokens():
        message = 'Проблемы с переменными окружения'
        raise SystemExit(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_response = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            if check_response(response):
                message = parse_status(response['homeworks'][0])
                check_msg = checking_repeated_messages(message, last_response)
                if check_msg is not None:
                    last_response = check_msg
                    send_message(bot, message)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Ошибка в работе программы: {error}'
            logger.error(message)
            check_msg = checking_repeated_messages(message, last_response)
            if check_msg is not None:
                last_response = check_msg
                send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
