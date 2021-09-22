FROM python:3.9-buster

WORKDIR /lexie
COPY . /lexie

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install memcached

CMD ["uwsgi", "app.ini"]
