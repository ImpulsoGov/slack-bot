
<!--
SPDX-FileCopyrightText: 2021, 2022 ImpulsoGov <contato@impulsogov.org>

SPDX-License-Identifier: MIT
-->
![Badge em Produção](https://img.shields.io/badge/status-em%20produ%C3%A7%C3%A3o-green)

# Slack Bot

Automação de envio de notificações de logs e mensagens sobre transmissor tendo como destino canais do Slack da ImpulsoGov


*******
## :mag_right: Índice
1. [Contexto](#contexto)
2. [Estrutura do repositório](#estrutura)
3. [Rodando em produção](#rodando)
4. [Instruções para instalação e acesso ao projeto](#instalacao)
5. [Contribua](#contribua)
6. [Licença](#licenca)
*******


<div id='contexto'/>  

## :rocket: Contexto
A ImpulsoGov desenvolveu um transmissor de dados que conecta o servidor PEC municipal com nosso banco a fim de transmitir dados nominais para o desenvolvimento do projeto de busca ativa. O primeiro modelo de transmissão necessitou de acompanhamento frequente quanto ao sucesso de sua operação. O Slack Bot nasceu da necessidade de gerar notificações emergentes de operações que ocorrem no banco da ImpulsoGov aos canais do Slack. 


*******
  
  
 <div id='estrutura'/>  
 
 ## :milky_way: Estrutura do repositório


```plain

├─ slack-bot
│  ├─ transmissor_bot
│  ├─ utilitarios
└─ ...
```


*******
 <div id='rodando'/> 
 
## :gear: Rodando em produção
O pacote utiliza ações do
[GitHub Actions](https://docs.github.com/actions) para enviar imagens para o
[DockerHub da Impulso Gov](https://hub.docker.com/orgs/impulsogov/repositories)
sempre que há uma atualização da branch principal do repositório. Diariamente,
essa imagem é baixada para uma máquina virtual que executa as capturas
pendentes.

Para executar os pacotes em produção, defina as credenciais necessárias como [segredos no repositório](https://docs.github.com/en/actions/security-guides/encrypted-secrets). Se necessário, ajuste os arquivos do diretório [.github/workflows](./.github/workflows).

*******

<div id='instalacao'/> 

 ## 🛠️ Instruções para instalação e acesso ao projeto

Antes de rodar o container com o pacote localmente, crie um arquivo nomeado `.env` na raiz do repositório. Esse arquivo deve conter as credenciais de acesso ao banco de dados e outras configurações de execução do projeto. Você pode utilizar o modelo do arquivo `.env.sample` como referência.

Em seguida, execute os comandos abaixo em um terminal de linha de comando (a execução completa pode demorar):

```sh
$ docker build -t slackbot .
$ docker run -p 8888:8888 slackbot:latest
```

*******

<div id='contribua'/>  

## :left_speech_bubble: Contribua
Sinta-se à vontade para contribuir em nosso projeto! Abra uma issue ou crie um fork do projeto e envie sua contribuição como um novo pull request.


*******
<div id='licenca'/>  

## :registered: Licença
MIT (c) 2020, 2022 Impulso Gov <contato@impulsogov.org>
