# scrap-carros

## Sobre o projeto

O scrap-carros é uma API REST desenvolvida para reunir em um único lugar anúncios de carros coletados de diversos sites de venda. O objetivo é realizar a raspagem automática de dados em múltiplos portais, consolidar as informações e disponibilizá-las através de uma API, permitindo comparar preços e modelos sem precisar acessar cada site individualmente.

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy (async)
- PostgreSQL 16
- Docker

## Pré-requisitos

- Docker Desktop

## Rodando o projeto

```bash
make run back
```

Isso sobe os 3 containers: banco de dados, API e pgAdmin.

| Serviço | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 |

## Comandos disponíveis

```bash
make run back   # sobe os containers em background
make build      # reconstrói a imagem e sobe
make down       # para todos os containers
make logs       # acompanha os logs do backend
```

## Variáveis de ambiente

Copie o arquivo de exemplo e ajuste se necessário:

```bash
cp .env.example .env
```

## Acessar o pgAdmin

- URL: http://localhost:5050
- Email: `admin@admin.com`
- Senha: `admin`
- Conexão com o banco: Host `localhost`, Port `7777`, User `paulo`, Senha `paulo2131`
