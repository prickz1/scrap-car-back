import asyncio

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


@router.get("/carros")
async def carros(marca: str, modelo: str, ano: int):
    df = await asyncio.to_thread(_df)
    filtrado = df[
        (df["marca"] == marca) &
        (df["modelo"] == modelo) &
        (df["ano"] == ano) &
        df["preco"].notna()
    ]
    cols = ["id", "preco", "quilometragem", "cambio", "combustivel", "cor", "direcao"]
    return dados.df_to_records(filtrado[cols])


@router.get("/avaliar/{carro_id}")
async def avaliar(carro_id: int):
    df = await asyncio.to_thread(_df)
    carro = df[df["id"] == carro_id]
    if carro.empty:
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    def _calcular():
        previsoes = ml_model.prever(carro)
        serie_geral = previsoes["geral"]
        if serie_geral.isna().all():
            return None

        preco_real = float(carro["preco"].iloc[0])
        preco_geral = round(float(serie_geral.iloc[0]))

        resultado = {
            "id": carro_id,
            "preco_real": round(preco_real),
            "geral": {
                "preco_previsto": preco_geral,
                "desconto": preco_geral - round(preco_real),
            },
        }

        if "popular" in previsoes:
            serie_popular = previsoes["popular"]
            if not serie_popular.isna().all():
                preco_popular = round(float(serie_popular.iloc[0]))
                resultado["popular"] = {
                    "preco_previsto": preco_popular,
                    "desconto": preco_popular - round(preco_real),
                }

        return resultado

    result = await asyncio.to_thread(_calcular)
    if result is None:
        raise HTTPException(status_code=422, detail="Dados insuficientes para previsão")
    return result
