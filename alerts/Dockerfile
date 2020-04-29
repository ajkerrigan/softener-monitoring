FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN python3 -m pip install -r requirements.txt

COPY . /app
ENTRYPOINT [ "gunicorn" ]
CMD [ "--bind", "0.0.0.0:80", "app:app" ]
