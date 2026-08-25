import asyncio
import time
from app.core.database import engine
from app.services.scraper.config import TOTAL_PAGINAS, MAX_LOTES
from app.services.scraper.navegador import pegar_anuncios
from app.services.scraper.persistencia import salvar_anuncios

engine.echo = False


async def executar():
    anuncios, falhados = await pegar_anuncios()
    print("Salvando no banco...")
    salvamento = await salvar_anuncios(anuncios)
    return anuncios, falhados, salvamento


if __name__ == "__main__":
    inicio = time.perf_counter()
    anuncios, falhados, salvamento = asyncio.run(executar())
    tempo_gasto = time.perf_counter() - inicio

    print("=" * 50)
    print(f"TOTAL COLETADO: {len(anuncios)} anúncios ({TOTAL_PAGINAS} páginas/lote | máx {MAX_LOTES} lotes)")
    print(f"FALHADOS:        {falhados}")
    print(f"SALVOS NO BANCO: {salvamento['salvos']}")
    print(f"DUPLICADOS:      {salvamento['duplicados']}")
    print(f"TEMPO GASTO:     {tempo_gasto:.2f} segundos")
    print("=" * 50)
