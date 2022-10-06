# SPDX-FileCopyrightText: 2021, 2022 ImpulsoGov <contato@impulsogov.org>
# SPDX-License-Identifier: MIT


FROM python:3.8.13-slim-bullseye

WORKDIR /app

ADD . /app

COPY ./requirements.txt /etc



RUN \
 apt-get clean all -qq && \
 apt-get update -yqq && \
 apt-get dist-upgrade -yqq && \
 apt-get autoremove -yqq && \
 python3 -m pip install --upgrade pip && \
 apt-get -y install libpq-dev gcc && \
 apt-get install -yqq git build-essential libssl-dev libffi-dev python3-dev cargo && \
 pip install -r /etc/requirements.txt

ENV IMPULSOETL_AMBIENTE desenvolvimento
ENV IMPULSOETL_BD_HOST bd_host
ENV IMPULSOETL_BD_PORTA bd_porta
ENV IMPULSOETL_BD_NOME bd_nome
ENV IMPULSOETL_BD_USUARIO bd_user
ENV IMPULSOETL_BD_SENHA bd_senha
ENV TOKEN_SLACK_APP_TRANSMISSOR token_slack
ENV CANAL_SLACK_APP slack_app

# Run app.py when the container launches
CMD ["python", "app.py"]
