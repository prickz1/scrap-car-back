# scrap-carros

## Sobre o projeto

TCC — sistema que raspa anúncios de carros da OLX, armazena em banco de dados e usa Machine Learning para estimar o preço justo de cada veículo. O usuário escolhe marca, modelo, ano e anúncio em uma interface web e vê se o carro está barato ou caro em relação ao que o modelo prevê.

## Stack

- **Python 3.14**
- **FastAPI** — API REST (scraping + ML)
- **SQLAlchemy async + asyncpg** — acesso ao banco
- **PostgreSQL 16** — armazenamento dos anúncios
- **scikit-learn** — GradientBoostingRegressor
- **pandas** — preparação de dados e inferência
- **Streamlit** — interface web (pasta `scrap-car-front/`)
- **Docker / Docker Compose** — orquestração

## Estrutura

```
scrap-car-back/
├── app/
│   ├── core/            → config e conexão com banco
│   ├── models/          → tabela cars (SQLAlchemy)
│   ├── services/scraper → raspagem da OLX
│   ├── ml/
│   │   ├── modelo.py    → carrega .pkl e faz previsão
│   │   └── dados.py     → lê banco → DataFrame em memória
│   └── api/routes/
│       ├── cars.py      → CRUD de carros
│       └── ml.py        → /ml/marcas, /ml/avaliar/{id} …
├── treino/
│   ├── database.py      → conexão direta ao banco (sync)
│   ├── preparar_dados.py→ filtra outliers, codifica features
│   └── treinar_gb.py    → treina e salva os .pkl
├── modelos/             → gb_modelo.pkl + gb_encoder.pkl (não versionados)
├── docker-compose.yml
├── Dockerfile
└── Makefile
```

## Pré-requisitos

- Docker Desktop instalado e rodando
- Python 3.14
- Dependências instaladas:

```bash
pip install -r requirements.txt
```

## Rodando do zero

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

### 2. Subir banco de dados e API

```bash
make back
```

Sobe o PostgreSQL na porta `7777` e a API na porta `8000`.

### 3. Popular o banco (scraping)

```bash
make scrape        # raspa anúncios da OLX
make enrich        # enriquece dados faltantes
make enrich-detail # enriquece detalhes adicionais
make clean-scrap   # remove registros com erro de scraping
```

> O scraping pode demorar várias horas dependendo do volume.

### 4. Treinar o modelo de ML

Com o banco populado:

```bash
make treinar
```

Conecta em `localhost:7777`, treina um **GradientBoostingRegressor** com 30.000 árvores e salva os arquivos em `modelos/`. Demora aproximadamente 1–2 horas. R² esperado: ~0.86.

### 5. Reiniciar a API para carregar o modelo

```bash
make down
make back
```

No boot a API carrega os `.pkl` automaticamente via volume Docker.

### 6. Rodar o front

```bash
cd ../scrap-car-front
make run
```

Abre em `http://localhost:8501`.

## Resumo dos comandos

| Ordem | Comando | O que faz |
|-------|---------|-----------|
| 1 | `make back` | Sobe banco + API |
| 2 | `make scrape` → `enrich` → `clean-scrap` | Popula o banco |
| 3 | `make treinar` | Treina o modelo ML |
| 4 | `make down && make back` | Reinicia API com modelo carregado |
| 5 | `cd ../scrap-car-front && make run` | Sobe o front |

## Serviços

| Serviço | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| PostgreSQL | localhost:7777 |

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL de conexão com o banco | PostgreSQL via Docker |
| `APP_NAME` | Nome da aplicação | `Scrap Carros API` |
| `ML_MODELS_DIR` | Caminho dos `.pkl` dentro do container | `/app/modelos_ml` |
