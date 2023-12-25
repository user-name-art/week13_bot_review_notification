FROM python:3.11.7-slim-bookworm
WORKDIR /app
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY . /app/
CMD [ "python", "bot.py" ]
