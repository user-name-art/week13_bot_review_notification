# Отправляем уведомления о проверке работ

Скрипт отслеживает изменение статуса проверки работ на сайте [Devman](https://dvmn.org) и отправляет соответствующее уведомление с помощью Telegram-бота.

## Как установить

Скачайте код
```
https://github.com/user-name-art/week13_bot_review_notification.git
```
При необходимости создайте виртуальное окружение. Например: 
```
python -m venv .venv
``` 
Установите зависимости:
```
pip install -r requirements.txt
```

## Как запустить

Для работы понадобится файл **.env** (смотри **.env.template** для примера). 
* **DEVMAN_TOKEN** персональный токен пользователя на сайте [Devman](https://dvmn.org).
* **DEVMAN_TIMEOUT** время ожидания ответа от сайта [Devman](https://dvmn.org). Если начение не указано, скрипт будет ждать 100 секунд.
* **TG_BOT_TOKEN** токен Telegram-бота.
* **TG_CHAT** chat_id пользователя в Telegram. Можно узнать, написав в Telegram специальному боту [@userinfobot](https://telegram.me/userinfobot).

Запустите скрипт:
```
python bot.py
```
## Docker

Можно запустить бота как Docker-контейнер. Для этого нужно перейти в терминале в папку проекта и выполнить следующие шаги.

Сначала создаем Docker-образ. **bot-review-notification** в данном случае - это имя образа.

```
docker build -t bot-review-notification .
```
Далее на основе полученного образа создаем Docker-контейнер и запускаем его. В приведенном примере понадобится файл **.env**, структура которого описана выше. Также можно передать все необходимые параметры в командной строке (см. [документацию](https://docs.docker.com/engine/reference/commandline/run/#env)).

```
docker run -d --env-file .env bot-review-notification
``````

После этого контейнер появится в списке запущенных. Проверяем: 

```
docker ps
```

Если контейнер почему-то не стартовал, ищем его ID:

```
docker container ls -a -s
```

И смотрим логи:

```
docker logs <container_id>
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
