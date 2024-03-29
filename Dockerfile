FROM python:3-buster

WORKDIR /usr/src/app

RUN pip install Events~=0.4 paho-mqtt~=1.5.1 PyYAML~=6.0.1

COPY . .

CMD [ "python", "./main.py" ]
