FROM python:3.9-alpine
ENV PYTHONUNBUFFERED=1
#RUN apt update && apt install -y python3 python3-pip

ADD requirements.txt /requirements.txt

RUN pip install -r /requirements.txt
