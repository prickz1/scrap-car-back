import json

import pandas as pd
from sqlalchemy import create_engine

IDS_IGNORAR = [79641, 159336, 794481, 79645, 76207, 76183, 79626, 79521,
               79214, 79623, 79627, 79497, 79646, 79628, 79630, 71351,
               64802, 79624, 79629, 79351, 79631, 79659]

_df: pd.DataFrame | None = None
_engine = None


def _sync_engine(database_url: str):
    global _engine
    if _engine is None:
        sync_url = database_url.replace("+asyncpg", "+psycopg2").replace("+aiosqlite", "")
        _engine = create_engine(sync_url)
    return _engine


def carregar_df(database_url: str) -> pd.DataFrame:
    global _df
    if _df is None:
        engine = _sync_engine(database_url)
        df = pd.read_sql("""
            SELECT id, preco, ano, quilometragem, modelo,
                   marca, combustivel, cambio,
                   cor, tipo_veiculo, direcao
            FROM cars
            WHERE preco IS NOT NULL
              AND marca IS NOT NULL
              AND marca != 'ERRO'
        """, engine)
        df = df[~df["id"].isin(IDS_IGNORAR)]
        s_km = df["quilometragem"].dropna()
        lim_km = s_km.quantile(0.75) + 1.5 * (s_km.quantile(0.75) - s_km.quantile(0.25))
        df = df[df["quilometragem"].isna() | (df["quilometragem"] <= lim_km)]
        df["idade_veiculo"] = 2026 - df["ano"]
        _df = df
    return _df


def df_to_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records"))
