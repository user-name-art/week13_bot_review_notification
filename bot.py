import telegram
import logging
import time
import requests

from environs import Env


URL = 'https://dvmn.org/api/long_polling/'


def get_lesson_review(server_answer):
    lesson_title = server_answer['new_attempts'][0]['lesson_title']
    lesson_url = server_answer['new_attempts'][0]['lesson_url']

    if server_answer['new_attempts'][0]['is_negative']:
        lesson_assessment = 'К сожалениию, в работе нашлись ошибки.'
    else:
        lesson_assessment = 'Преподавателю все понравилось, можно приступать к следующему уроку.'
    
    return lesson_title, lesson_url, lesson_assessment


def main():
    env = Env()
    env.read_env()

    logger = logging.getLogger('ReviewNotifications')
    logger.setLevel(logging.INFO)
    
    handler = logging.FileHandler('logs.log')
 
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)

    BOT_TOKEN = env.str('TG_BOT_TOKEN')
    CHAT_ID = env.str('TG_CHAT')
    DEVMAN_TOKEN = env.str('DEVMAN_TOKEN')
    DEVMAN_TIMEOUT = env.int('DEVMAN_TIMEOUT', 100)
    
    params = {'timeout': DEVMAN_TIMEOUT}
    headers = {'Authorization': f'Token {DEVMAN_TOKEN}'}

    bot = telegram.Bot(token=BOT_TOKEN)

    while True:
        try:
            logger.info('start!')
            response = requests.get(URL, headers=headers, params=params)
            response.raise_for_status()

            server_answer = response.json()

            if server_answer['status'] == 'timeout':
                params['timestamp'] = server_answer['timestamp_to_request']
            elif server_answer['status'] == 'found':
                params['timestamp'] = server_answer['last_attempt_timestamp']
                
                lesson_title, lesson_url, lesson_assessment = get_lesson_review(server_answer)

                bot.send_message(chat_id=CHAT_ID,
                                text=f'Преподаватель проверил работу "{lesson_title}". \n \n {lesson_url} \n \n {lesson_assessment}'
                                )

        except requests.exceptions.ReadTimeout:
            logger.info('time out')
        except requests.exceptions.ConnectionError:
            logger.info('ConnectionError')
            time.sleep(2)


if __name__ == '__main__':
    main()
