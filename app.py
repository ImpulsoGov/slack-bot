# SPDX-FileCopyrightText: 2021, 2022 ImpulsoGov <contato@impulsogov.org>
#
# SPDX-License-Identifier: MIT


""" Scrpits de notificação automática para canais do slack ."""

from __future__ import annotations

from bd import Sessao
from transmissor_bot.principal import obter_falhas_transmissor



if __name__ == "__main__":
    with Sessao() as sessao:
        obter_falhas_transmissor(sessao=sessao)