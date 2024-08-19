FROM python:3.12-slim

RUN adduser --disabled-password --gecos '' appuser
RUN usermod -a -G sudo appuser

RUN apt update -y && apt upgrade -y
RUN apt install -y libpq-dev gcc
RUN pip install --upgrade pip 

RUN mkdir /usr/src/setup
ADD ./requirements.txt /usr/src/setup
WORKDIR /usr/src/setup
RUN pip install --upgrade -r requirements.txt 

COPY --chmod=755 ./start.sh /usr/src/setup/
RUN chown appuser:appuser /usr/src/setup/start.sh
RUN chmod +x /usr/src/setup/start.sh

#USER = appuser

RUN mkdir /home/appuser/app
ADD ./src /home/appuser/app
WORKDIR /home/appuser/app