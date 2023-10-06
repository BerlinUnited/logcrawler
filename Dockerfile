FROM ubuntu:22.04

RUN apt install -y python3 python3-pip

ADD main.py /code/main.py
ADD requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

CMD [ "python", "/code/main.py" ]