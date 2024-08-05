FROM python:3.12-slim
RUN apt update -y && apt upgrade -y
RUN apt install -y libpq-dev gcc zip whois
RUN pip install --upgrade pip 
RUN mkdir /usr/src/setup
ADD ./requirements.txt /usr/src/setup
WORKDIR /usr/src/setup
RUN pip install --upgrade -r requirements.txt 
RUN mkdir /usr/src/app
ADD ./src /usr/src/app
RUN chmod +x /usr/src/app/start.sh
WORKDIR /usr/src/app