# SPDX-FileCopyrightText: 2021, 2022 ImpulsoGov <contato@impulsogov.org>
#
# SPDX-License-Identifier: MIT


""" Verifica transmissores que não realização transmissão de dados na data agendada e cria mensagem de notificação"""

from __future__ import annotations

from sqlalchemy.orm import Session,Query
from datetime import datetime
from pytz import timezone
import sys 

sys.path.append(r"\slack-bot")
from bd import tabelas
from loggers import logger

fuso_horario = timezone("America/Sao_Paulo")
tabela_monitoramento_transmissoes = "configuracoes.monitoramento_transmissoes"


def cria_mensagem(
    municipio_uf: str,
    lista_nominal: str,
    ultima_tranmissao: datetime,
    transmissao_atrasao_dias: datetime,
) -> list:
    """ Cria mensagem no formato block a ser consumida pela API do Slack.
        Argumentos:
            municipio_uf: Nome do município e sigla da unidade federativa
            lista_nominal: Nome da lista nominal de referência do produto
            ultima_tranmissao: Data e hora da última transmissão realizada
            transmissao_atrasao_dias: Quantidade de horas e ou dias atrasadas em relação a última transmissão
        Retorna:
            Mensagem no formato block para ser listada
        [`sqlalchemy.orm.session.Session`]: https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
        """

    mensagem = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Transmissão atrasada  :large_yellow_circle::large_yellow_circle::large_yellow_circle:",
            },
        },
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Municipio* : {municipio_uf} \n*Lista nominal* : {lista_nominal} \n*Última transmissão* : {ultima_tranmissao} \n*Tempo de atraso* : {transmissao_atrasao_dias}",
                }
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Marque a mensagem com  :eyes:  se já foi verificada e  :white_check_mark:  se já foi resolvida",
            },
        },
        {"type": "divider"},
    ]

    return mensagem


def consulta_erros_agendamentos(
    sessao: Session, 
    tabela_destino: str,
) -> Query:
    """Obtém lista de registro de transmissores com agendamentos não realizadas na data prevista.
    Argumentos:
        sessao: objeto [`sqlalchemy.orm.session.Session`][] que permite
        acessar a base de dados da ImpulsoGov.
        tabela_destino: Tabela que será consultado os registros.
    Retorna:
        Lista de tranmissores com agendamentos não realizadas na data prevista
        e aplicação.
    [`sqlalchemy.orm.session.Session`]: https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
    """

    tabela = tabelas[tabela_destino]
    return (
        sessao.query(tabela)
            .filter(tabela.c.status_transmissao == 'Transmissão atrasada')
            .all()
            )


def processa_transmissoes_atrasadas(sessao: Session) -> list:

    """ Processa trasmissões com atrasos e cria mensagem de erro a ser transmitida.
    Argumentos:
        sessao: objeto [`sqlalchemy.orm.session.Session`][] que permite
        acessar a base de dados da ImpulsoGov.
    Retorna:
        Lista de mensagens a ser transmitidas via Slack
    [`sqlalchemy.orm.session.Session`]: https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
    """

    logger.info("Verificando registros transmissões não realizadas")
    registros = consulta_erros_agendamentos(
        sessao=sessao, 
        tabela_destino=tabela_monitoramento_transmissoes
    )
    if registros is not None:
        lista_mensagem = []
        for registro in registros:
    
            ultima_tranmissao = registro.ultima_tranmissao.astimezone(fuso_horario)
            # NOTE: formata data/hora no fuso horário de São Paulo
            ultima_tranmissao = ultima_tranmissao.strftime("%d/%m/%Y %H:%M:%S")

            logger.info("Criando mensagem a ser notificado por canal do Slack")
            mensagem = cria_mensagem(
                municipio_uf=registro.municipio_uf,
                lista_nominal=registro.lista_nominal,
                ultima_tranmissao=ultima_tranmissao,
                transmissao_atrasao_dias=registro.transmissao_atrasao_dias,
            )
            lista_mensagem.append(mensagem)
        return lista_mensagem
