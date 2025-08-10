FROM rust:1.89 AS builder

# Install Python and maturin in the builder stage
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . .

RUN python3 --version

# Install maturin
RUN python3 -m pip install pip --upgrade --break-system-packages && python3 -m pip install -r requirements.txt --break-system-packages




RUN maturin build --release
RUN ls