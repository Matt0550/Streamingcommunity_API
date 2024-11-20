# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /home

ARG APP_USER=appuser
ENV APP_USER=${APP_USER}
ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -M -s /usr/sbin/nologin ${APP_USER}

RUN apt-get update && apt-get install -y gosu dos2unix

# Install build tools
RUN apt-get install -y build-essential

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .

RUN dos2unix /home/scripts/init.sh

RUN chmod +x /home/scripts/init.sh

RUN chown -R ${APP_USER}:${APP_USER} /home

EXPOSE 5000

ENTRYPOINT [ "/bin/bash", "/home/scripts/init.sh" ]