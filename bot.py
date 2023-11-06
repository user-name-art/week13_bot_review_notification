import telegram
import logging
import time
import requests

from environs import Env


def get_lesson_summary(server_answer):
    lesson_title = server_answer['new_attempts'][0]['lesson_title']
    lesson_url = server_answer['new_attempts'][0]['lesson_url']

    if server_answer['new_attempts'][0]['is_negative']:
        lesson_assessment = 'К сожалениию, в работе нашлись ошибки.'
    else:
        lesson_assessment = 'Преподавателю все понравилось, можно приступать к следующему уроку.'
    
    return f'Преподаватель проверил работу "{lesson_title}". \n \n {lesson_url} \n \n {lesson_assessment}'


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(level=logging.INFO, filename='log.log', format='%(asctime)s %(levelname)s %(message)s')

    URL = 'https://dvmn.org/api/long_polling/'
    BOT_TOKEN = env.str('TG_BOT_TOKEN')
    CHAT_ID = env.str('TG_CHAT')
    DEVMAN_TOKEN = env.str('DEVMAN_TOKEN')
    DEVMAN_TIMEOUT = env.int('DEVMAN_TIMEOUT', 100)
    
    params = {}
    headers = {'Authorization': f'Token {DEVMAN_TOKEN}'}

    bot = telegram.Bot(token=BOT_TOKEN)

    while True:
        try:
            response = requests.get(URL, headers=headers, params=params, timeout=DEVMAN_TIMEOUT)
            response.raise_for_status()

            server_answer = response.json()

            if server_answer['status'] == 'timeout':
                params['timestamp'] = server_answer['timestamp_to_request']
            elif server_answer['status'] == 'found':
                params['timestamp'] = server_answer['last_attempt_timestamp']
                logging.info('Статус проверки работы изменился')
                
                lesson_summary = get_lesson_summary(server_answer)

                bot.send_message(chat_id=CHAT_ID, text=lesson_summary)

        except requests.exceptions.ReadTimeout:
            logging.error('ReadTimeout')
        except requests.exceptions.ConnectionError:
            logging.error('ConnectionError')
            time.sleep(30)


if __name__ == '__main__':
    main()
