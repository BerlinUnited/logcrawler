FROM python:3.11

ENV PYTHONUNBUFFERED=1

ADD requirements.txt /requirements.txt
ADD *.py /
ADD run_all.sh /run_all.sh
RUN pip install -r /requirements.txt

