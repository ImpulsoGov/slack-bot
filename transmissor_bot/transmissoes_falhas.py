# SPDX-FileCopyrightText: 2021, 2022 ImpulsoGov <contato@impulsogov.org>
#
# SPDX-License-Identifier: MIT


""" Verifica erros de execução na transmissão de dados na data agendada e cria mensagem de notificação"""

from __future__ import annotations

from sqlalchemy.orm import Session,Query
from datetime import datetime
from pytz import timezone
import sys 

sys.path.append(r"\slack-bot")
from bd import tabelas
from loggers import logger

fuso_horario = timezone("America/Sao_Paulo")

tabela_historico_capturas = "busca_ativa.historico_capturas"


def cria_mensagem(
    execucao_data_hora: datetime,
    municipio_id_sus: str,
    mensagem_titulo: str,
    contexto: str,
) -> list:

    """ Cria mensagem no formato block a ser consumida pela API do Slack.
            Argumentos:
                execucao_data_hora: Data e hora da tentativa de transmissão
                municipio_id_sus: Código IBGE SUS do município
                mensagem_titulo: Mensagem título do erro gerado
                contexto: Log do erro gerado
            Retorna:
                Mensagem no formato block para ser listada
            [`sqlalchemy.orm.session.Session`]: https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
            """

    mensagem = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Erro na transmissão dos dados :red_circle::red_circle::red_circle:",
            },
        },
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Codigo do Município* : {municipio_id_sus} \n*Data/Hora de execução* : {execucao_data_hora} \n*Mensagem de erro* : {mensagem_titulo} \n*Contexto de erro* : {contexto}",
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


def consulta_erros_transmissor(
    sessao: Session, 
    tabela_destino: str
) -> Query:

    """Obtém lista de erros de transmissão na tabela historico_capturas.
    Argumentos:
        sessao: objeto [`sqlalchemy.orm.session.Session`][] que permite
        acessar a base de dados da ImpulsoGov.
        tabela_destino: Tabela que será consultado os registros.
    Retorna:
        Lista de transmissores com erros de execução
        e aplicação.
    [`sqlalchemy.orm.session.Session`]: https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
    """

    tabela = tabelas[tabela_destino]
    return (
        sessao.query(tabela)
        .filter(tabela.c.mensagem != "Trasmissão realizada com sucesso")
        .filter(tabela.c.erro_transmitido == False)
        .all()
    )


def atualiza_status_erro(
    sessao: Session, 
    tabela_destino: str
 )-> None:

    """ Marca registro de erro como lido na tabela historico_capturas.
        Argumentos:
            sessao: objeto [`sqlalchemy.orm.session.Session`][] que permite
            acessar a base de dados da ImpulsoGov.
            tabela_destino: Tabela que terá o registro atualizado.
        """

    tabela = tabelas[tabela_destino]
    sessao.query(tabela).filter(tabela.c.mensagem != "Trasmissão realizada com sucesso").update({"erro_transmitido": True})


def processa_transmissoes_com_falhas(sessao: Session) -> list:

    """ Processa trasmissões com falhas e cria mensagem de erro a ser transmitida.
    Argumentos:
        sessao: objeto [`sqlalchemy.orm.session.Session`][] que permite
        acessar a base de dados da ImpulsoGov.
    Retorna:
        Lista de mensagens a ser transmitidas via Slack
    [`sqlalchemy.orm.session.Session`]: https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
    """

    logger.info("Verificando registros de erros durante operação de transmissão dos dados")
    registros = consulta_erros_transmissor(
        sessao=sessao, tabela_destino=tabela_historico_capturas
    )
    if registros is not None:
        lista_mensagem = []
        for registro in registros:

            execucao_data_hora = registro.execucao_data_hora.astimezone(fuso_horario)
            # NOTE: formata data/hora no fuso horário de São Paulo
            execucao_data_hora = execucao_data_hora.strftime("%d/%m/%Y %H:%M:%S")

            logger.info("Criando mensagem a ser notificado por canal do Slack")
            mensagem = cria_mensagem(
                execucao_data_hora=execucao_data_hora,
                municipio_id_sus=registro.municipio_id_sus,
                mensagem_titulo=registro.mensagem,
                contexto=registro.erro_contexto,
            )
            logger.info("Marcando mensagem de erro como já lida")
            atualiza_status_erro(
                sessao=sessao, tabela_destino=tabela_historico_capturas
            )
            lista_mensagem.append(mensagem)
        return lista_mensagem
