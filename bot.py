import telegram
import logging
import time
import requests

from environs import Env


DEVMAN_URL = 'https://dvmn.org/api/long_polling/'


def get_lesson_summary(response_object):
    lesson_title = response_object['new_attempts'][0]['lesson_title']
    lesson_url = response_object['new_attempts'][0]['lesson_url']

    if response_object['new_attempts'][0]['is_negative']:
        lesson_assessment = 'К сожалениию, в работе нашлись ошибки.'
    else:
        lesson_assessment = 'Преподавателю все понравилось, можно приступать к следующему уроку.'
    
    return f'Преподаватель проверил работу "{lesson_title}". \n \n {lesson_url} \n \n {lesson_assessment}'


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(level=logging.INFO, filename='log.log', format='%(asctime)s %(levelname)s %(message)s')

    bot_token = env.str('TG_BOT_TOKEN')
    chat_id = env.str('TG_CHAT')
    devman_token = env.str('DEVMAN_TOKEN')
    devman_timeout = env.int('DEVMAN_TIMEOUT', 100)
    
    params = {}
    headers = {'Authorization': f'Token {devman_token}'}

    bot = telegram.Bot(token=bot_token)

    while True:
        try:
            response = requests.get(DEVMAN_URL, headers=headers, params=params, timeout=devman_timeout)
            response.raise_for_status()

            response_object = response.json()

            if response_object['status'] == 'timeout':
                params['timestamp'] = response_object['timestamp_to_request']
            elif response_object['status'] == 'found':
                params['timestamp'] = response_object['last_attempt_timestamp']
                logging.info('Статус проверки работы изменился')
                
                lesson_summary = get_lesson_summary(response_object)

                bot.send_message(chat_id=chat_id, text=lesson_summary)

        except requests.exceptions.ReadTimeout:
            logging.error('ReadTimeout')
        except requests.exceptions.ConnectionError:
            logging.error('ConnectionError')
            time.sleep(30)


if __name__ == '__main__':
    main()
