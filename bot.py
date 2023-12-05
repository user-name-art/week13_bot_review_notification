import telegram
import logging
import time
import requests

from environs import Env


DEVMAN_URL = 'https://dvmn.org/api/long_polling/'


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.bot_token = bot_token
        self.tg_bot = telegram.Bot(token=bot_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_lesson_summary(review_summary):
    lesson_title = review_summary['new_attempts'][0]['lesson_title']
    lesson_url = review_summary['new_attempts'][0]['lesson_url']

    if review_summary['new_attempts'][0]['is_negative']:
        lesson_assessment = 'К сожалениию, в работе нашлись ошибки.'
    else:
        lesson_assessment = 'Преподавателю все понравилось, можно приступать к следующему уроку.'
    
    return f'Преподаватель проверил работу "{lesson_title}". \n \n {lesson_url} \n \n {lesson_assessment}'


def main():
    env = Env()
    env.read_env()

    bot_token = env.str('TG_BOT_TOKEN')
    chat_id = env.str('TG_CHAT')
    devman_token = env.str('DEVMAN_TOKEN')
    devman_timeout = env.int('DEVMAN_TIMEOUT', 100)

    logger = logging.getLogger('Logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot_token, chat_id))
    
    params = {}
    headers = {'Authorization': f'Token {devman_token}'}

    bot = telegram.Bot(token=bot_token)
    logger.info('bot started')

    while True:
        try:
            response = requests.get(DEVMAN_URL, headers=headers, params=params, timeout=devman_timeout)
            response.raise_for_status()

            review_summary = response.json()

            if review_summary['status'] == 'timeout':
                params['timestamp'] = review_summary['timestamp_to_request']
            elif review_summary['status'] == 'found':
                params['timestamp'] = review_summary['last_attempt_timestamp']
                logger.info('Статус проверки работы изменился')
                lesson_summary = get_lesson_summary(review_summary)
                bot.send_message(chat_id=chat_id, text=lesson_summary)

        except requests.exceptions.ReadTimeout:
            logger.error('ReadTimeout')
        except requests.exceptions.ConnectionError:
            logger.error('ConnectionError')
            time.sleep(30)
        except Exception as err:
            logger.error('Возникла следующая ошибка:')
            logger.error(err, exc_info=True)


if __name__ == '__main__':
    main()
