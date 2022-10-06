# SPDX-FileCopyrightText: 2021, 2022 ImpulsoGov <contato@impulsogov.org>
#
# SPDX-License-Identifier: MIT


""" Scrpits de notificação automática para canais do slack ."""

from __future__ import annotations

import os
from typing import Final
from slack_sdk import WebClient
from sqlalchemy.orm import Session
import sys 

sys.path.append(r"\slack-bot")
from loggers import logger
from transmissor_bot.transmissoes_falhas import processa_transmissoes_com_falhas
from transmissor_bot.transmissoes_atrasadas import processa_transmissoes_atrasadas


TOKEN_SLACK_APP_TRANSMISSOR: Final[str | None] = os.getenv("TOKEN_SLACK_APP_TRANSMISSOR", None)
CANAL_SLACK_TRANSMISSOR: Final[str | None] = os.getenv("CANAL_SLACK_APP", None)
client = WebClient(TOKEN_SLACK_APP_TRANSMISSOR)


def captura_erros_transmissao(
    sessao: Session,
    teste: bool = False,
    ) -> None:
    """Junta etapas de checagem de agendamentos atrasado, criação da mensagem de notificação e envio da mensagem no Slack.

    Argumentos:
        sessao: objeto [`sqlalchemy.orm.session.Session`][] que permite
            acessar a base de dados da ImpulsoGov.
        teste: Indica se as modificações devem ser de fato escritas no banco de
            dados (`False`, padrão) e mensagens enviadas no Slack. Caso seja `True`,
            as modificações são adicionadas à uma transação, e podem ser revertidas 
            com uma chamada posterior ao método [`Session.rollback()`][] da sessão 
            gerada com o SQLAlchemy.
    """

    lista_mensagens_erros_execucao = processa_transmissoes_com_falhas(sessao=sessao)
    if lista_mensagens_erros_execucao is not None:
        for mensagem_erro_execucao in lista_mensagens_erros_execucao:

            logger.info("Enviando mensagem para o canal 'logs-transmissor'")

            if teste:
                break
            notificacao = client.chat_postMessage(
                channel=CANAL_SLACK_TRANSMISSOR,
                blocks=mensagem_erro_execucao if mensagem_erro_execucao else None,
            )
            sessao.commit()

            logger.info("Mensagem notificada")
            logger.info("Conteúdo da mensagem : {notificacao}",notificacao=notificacao)

def captura_agendamentos_atrasados(
    sessao: Session,
    teste: bool = False,
    )  -> None:
    """Junta etapas de checagem de agendamentos atrasado, criação da mensagem de notificação e envio da mensagem no Slack.

    Argumentos:
        sessao: objeto [`sqlalchemy.orm.session.Session`][] que permite
            acessar a base de dados da ImpulsoGov.
        teste: Indica se as modificações devem ser de fato escritas no banco de
            dados (`False`, padrão) e mensagens enviadas no Slack. Caso seja `True`,
            as modificações são adicionadas à uma transação, e podem ser revertidas 
            com uma chamada posterior ao método [`Session.rollback()`][] da sessão 
            gerada com o SQLAlchemy.
    """

    lista_mensagens_agendamentos_atrasados = processa_transmissoes_atrasadas(
        sessao=sessao
    )
    if lista_mensagens_agendamentos_atrasados is not None:
        for mensagem_agendamento_atrasado in lista_mensagens_agendamentos_atrasados:

            logger.info("Enviando mensagem para o canal 'logs-transmissor'")

            if teste:
                break
            notificacao = client.chat_postMessage(
                channel=CANAL_SLACK_TRANSMISSOR,
                blocks=mensagem_agendamento_atrasado if mensagem_agendamento_atrasado else None,
            )
            logger.info("Mensagem notificada")
            logger.info("Conteúdo da mensagem : {notificacao}",notificacao=notificacao)


def obter_falhas_transmissor(sessao: Session, teste: bool = False) -> None:
    """Executa todos os scripts de envio de logs para os canais do Slack.

    Argumentos:
        sessao: objeto [`sqlalchemy.orm.session.Session`][] que permite
            acessar a base de dados da ImpulsoGov.
        teste: Indica se as modificações devem ser de fato escritas no banco de
            dados (`False`, padrão) e mensagens enviadas no Slack. Caso seja `True`,
            as modificações são adicionadas à uma transação, e podem ser revertidas 
            com uma chamada posterior ao método [`Session.rollback()`][] da sessão 
            gerada com o SQLAlchemy.
    """
    captura_erros_transmissao(sessao=sessao,teste=teste)
    captura_agendamentos_atrasados(sessao=sessao,teste=teste)


