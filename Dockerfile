FROM python:3.11.7-slim-bookworm
WORKDIR /app
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --requirement /tmp/requirements.txt
COPY . /app/
CMD [ "python", "bot.py" ]
