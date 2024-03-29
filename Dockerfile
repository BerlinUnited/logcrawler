FROM scm.cms.hu-berlin.de:4567/berlinunited/naoth-2020:develop

ENV PYTHONUNBUFFERED=1
ENV NAOTH_REPO=/naoth/repo
ENV TOOLCHAIN_REPO=/naoth/toolchain

RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(. /etc/os-release && echo $UBUNTU_CODENAME)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg

RUN apt-get update && apt-get -y --no-install-recommends install \
    wget \
    git \
    python3 \
    python3-pip \
    nano \
    python-is-python3 \
    python3-dev \
    postgresql-client-16

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY image_extractor /scripts/image_extractor
COPY labelstudio_importer /scripts/labelstudio_importer
COPY representation_exporter /scripts/representation_exporter
COPY db_ingester /scripts/db_ingester
COPY check_images /scripts/check_images
COPY combine_images /scripts/combine_images
COPY minio_importer /scripts/minio_importer
COPY patch_exporter /scripts/patch_exporter