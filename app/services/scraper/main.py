import asyncio
import time
from app.core.database import engine
from app.services.scraper.navegador import pegar_anuncios
from app.services.scraper.persistencia import salvar_anuncios

engine.echo = False


async def executar():
    anuncios = await pegar_anuncios()
    print("Salvando no banco...")
    salvamento = await salvar_anuncios(anuncios)
    return anuncios, salvamento


if __name__ == "__main__":
    inicio = time.perf_counter()
    anuncios, salvamento = asyncio.run(executar())
    tempo_gasto = time.perf_counter() - inicio

    print("=" * 50)
    print(f"TOTAL COLETADO: {len(anuncios)} anúncios")
    print(f"SALVOS NO BANCO: {salvamento['salvos']}")
    print(f"DUPLICADOS (ignorados): {salvamento['duplicados']}")
    print(f"TEMPO GASTO: {tempo_gasto:.2f} segundos")
    print("=" * 50)
