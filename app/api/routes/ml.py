import asyncio

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.ml import dados
from app.ml import modelo as ml_model

router = APIRouter(prefix="/ml")


def _df():
    return dados.carregar_df(settings.DATABASE_URL)


@router.get("/marcas")
async def marcas():
    df = await asyncio.to_thread(_df)
    return sorted(df["marca"].dropna().unique().tolist())


@router.get("/modelos")
async def modelos(marca: str):
    df = await asyncio.to_thread(_df)
    return sorted(df[df["marca"] == marca]["modelo"].dropna().unique().tolist())


@router.get("/anos")
async def anos(marca: str, modelo: str):
    df = await asyncio.to_thread(_df)
    result = df[(df["marca"] == marca) & (df["modelo"] == modelo)]["ano"].dropna().unique().tolist()
    return sorted([int(a) for a in result], reverse=True)


@router.get("/cambios")
async def cambios(marca: str, modelo: str, ano: int):
    df = await asyncio.to_thread(_df)
    filtrado = df[(df["marca"] == marca) & (df["modelo"] == modelo) & (df["ano"] == ano)]
    return sorted(filtrado["cambio"].dropna().unique().tolist())


@router.get("/combustiveis")
async def combustiveis(marca: str, modelo: str, ano: int):
    df = await asyncio.to_thread(_df)
    filtrado = df[(df["marca"] == marca) & (df["modelo"] == modelo) & (df["ano"] == ano)]
    return sorted(filtrado["combustivel"].dropna().unique().tolist())


@router.get("/direcoes")
async def direcoes(marca: str, modelo: str, ano: int):
    df = await asyncio.to_thread(_df)
    filtrado = df[(df["marca"] == marca) & (df["modelo"] == modelo) & (df["ano"] == ano)]
    return sorted(filtrado["direcao"].dropna().unique().tolist())


@router.get("/anuncios")
async def anuncios(marca: str, modelo: str, ano: int, cambio: str, combustivel: str, direcao: str):
    df = await asyncio.to_thread(_df)
    filtrado = df[
        (df["marca"] == marca) &
        (df["modelo"] == modelo) &
        (df["ano"] == ano) &
        (df["cambio"] == cambio) &
        (df["combustivel"] == combustivel) &
        (df["direcao"] == direcao) &
        df["preco"].notna()
    ]
    cols = ["id", "preco", "quilometragem", "cor", "cidade", "estado", "titulo", "url_anuncio"]
    return dados.df_to_records(filtrado[cols].sort_values("preco"))


@router.get("/status")
async def status():
    return {"modelo_carregado": ml_model.esta_carregado()}


@router.get("/prever")
async def prever(
    marca: str,
    modelo: str,
    ano: int,
    cambio: str,
    combustivel: str,
    direcao: str,
    quilometragem: float,
):
    df = await asyncio.to_thread(_df)

    def _calcular():
        filtrado = df[
            (df["marca"] == marca) &
            (df["modelo"] == modelo) &
            (df["ano"] == ano)
        ]

        cor = filtrado["cor"].mode().iloc[0] if not filtrado.empty and filtrado["cor"].notna().any() else "Branco"
        tipo_veiculo = filtrado["tipo_veiculo"].mode().iloc[0] if not filtrado.empty and filtrado["tipo_veiculo"].notna().any() else "Hatch"

        entrada = pd.DataFrame([{
            "marca": marca,
            "modelo": modelo,
            "ano": ano,
            "idade_veiculo": 2026 - ano,
            "quilometragem": quilometragem,
            "cambio": cambio,
            "combustivel": combustivel,
            "direcao": direcao,
            "cor": cor,
            "tipo_veiculo": tipo_veiculo,
        }])

        previsoes = ml_model.prever(entrada)
        serie_geral = previsoes["geral"]
        if serie_geral.isna().all():
            return None

        resultado = {
            "geral": round(float(serie_geral.iloc[0])),
        }

        if "popular" in previsoes:
            serie_popular = previsoes["popular"]
            if not serie_popular.isna().all():
                resultado["popular"] = round(float(serie_popular.iloc[0]))

        return resultado

    if not ml_model.esta_carregado():
        raise HTTPException(status_code=503, detail="Modelo ainda carregando, tente em instantes")

    result = await asyncio.to_thread(_calcular)
    if result is None:
        raise HTTPException(status_code=422, detail="Dados insuficientes para previsão")
    return result
