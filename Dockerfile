FROM python:3.6-alpine
RUN mkdir /code
WORKDIR /code
RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers && (while true; do pip --no-cache-dir install uwsgi==2.0.18 && break; done)
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/