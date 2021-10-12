import os
import time
import requests
import logging
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filemode='w'
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 300
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена, в ней нашлись ошибки.'
}


def send_message(bot, message):
    logging.info(f'message send {message}')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def get_api_answer(url, current_timestamp):
    """Берем информацию от сервера."""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    print('!!!!!!!!!!!!!!!!!', homework_statuses.text)
    print('@@@@@@@@@@@@@@@', homework_statuses.status_code)
    logging.info('server respond')
    return homework_statuses.json()
    


def parse_status(homework):
    verdict = HOMEWORK_STATUSES[homework.get('status')]
    homework_name = homework.get('homework_name')
    logging.info(f'got verdict {verdict}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_response(response):
    hws = response.get('homeworks')
    return hws


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 0  #int(time.time())
    url = ENDPOINT
    while True:
        try:
            gaa = get_api_answer(url, current_timestamp)
            cr = check_response(gaa)
            if cr:
                for hw in cr:
                    ps = parse_status(hw)
                    send_message(bot, ps)
            time.sleep(RETRY_TIME)
        except Exception as error:
            logging.error('Bot down')
            bot.send_message(
                chat_id=CHAT_ID, text=f'Сбой в работе программы: {error}'
            )
            time.sleep(RETRY_TIME)
            continue


if __name__ == '__main__':
    main()
