FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       bash \
       ca-certificates \
       coreutils \
       findutils \
       gawk \
       git \
       grep \
       sed \
       tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ENV PYTHONUNBUFFERED=1
