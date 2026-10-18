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
        previsao = ml_model.prever(carro)
        if previsao.isna().all():
            return None

        preco_previsto = float(previsao.iloc[0])
        preco_real = float(carro["preco"].iloc[0])
        modelo_carro = carro["modelo"].iloc[0]

        similares = df[
            (df["modelo"] == modelo_carro) &
            (df["id"] != carro_id) &
            df["preco"].notna()
        ].copy()

        top5 = []
        if not similares.empty:
            similares["preco_previsto"] = ml_model.prever(similares)
            similares = similares[similares["preco_previsto"].notna()]
            similares["desconto"] = similares["preco_previsto"] - similares["preco"]
            cols = ["id", "ano", "preco", "preco_previsto", "desconto", "quilometragem", "cambio", "combustivel"]
            top5 = dados.df_to_records(similares.nlargest(5, "desconto")[cols])

        return {
            "id": carro_id,
            "preco_real": round(preco_real),
            "preco_previsto": round(preco_previsto),
            "desconto": round(preco_previsto - preco_real),
            "similares": top5,
        }

    result = await asyncio.to_thread(_calcular)
    if result is None:
        raise HTTPException(status_code=422, detail="Dados insuficientes para previsão")
    return result
