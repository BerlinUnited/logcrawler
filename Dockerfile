FROM ubuntu:22.04
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get -y --no-install-recommends install \
    wget \
    git \
    python3 \
    python3-pip

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
