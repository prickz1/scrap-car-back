import pandas as pd
from sqlalchemy import create_engine

_engine = create_engine("postgresql://paulo:paulo2131@localhost:7777/scrap_carros")


def carregar_dados() -> pd.DataFrame:
    return pd.read_sql("""
        SELECT id, preco, ano, quilometragem, modelo,
               marca, combustivel, cambio,
               cor, tipo_veiculo, direcao
        FROM cars
        WHERE preco IS NOT NULL
          AND marca IS NOT NULL
          AND marca != 'ERRO'
    """, _engine)
