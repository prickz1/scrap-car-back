import asyncio
import time
from playwright.async_api import async_playwright
from app.core.database import engine
from app.services.scraper.config import TOTAL_PAGINAS, MAX_LOTES
from app.services.scraper.navegador import criar_contexto, extrair_lote
from app.services.scraper.persistencia import salvar_anuncios

engine.echo = False


async def executar():
    total_salvos = 0
    total_duplicados = 0
    total_falhados = 0
    total_coletados = 0
    preco_minimo = None

    async with async_playwright() as p:
        browser, context, page = await criar_contexto(p)

        for lote in range(1, MAX_LOTES + 1):
            print(f"\n{'=' * 50}")
            print(f"Lote {lote}/{MAX_LOTES} | ps={preco_minimo or 'sem filtro'}")
            print(f"{'=' * 50}")

            anuncios, falhados = await extrair_lote(page, preco_minimo, lote)

            if not anuncios:
                print("\nNenhum anúncio encontrado. Encerrando coleta.")
                break

            print("\nSalvando lote no banco...")
            salvamento = await salvar_anuncios(anuncios)
            total_coletados += len(anuncios)
            total_salvos += salvamento["salvos"]
            total_duplicados += salvamento["duplicados"]
            total_falhados += falhados

            print(f"Lote {lote} concluído → salvos: {salvamento['salvos']} | duplicados: {salvamento['duplicados']}")
            print(f"Acumulado → {total_salvos} salvos | {total_duplicados} duplicados | {total_falhados} falhados")

            ultimo_preco = anuncios[-1]["preco"]
            if ultimo_preco == preco_minimo:
                print("Sem progresso de preço. Encerrando coleta.")
                break

            preco_minimo = ultimo_preco

            if lote < MAX_LOTES:
                print(f"\n[pausa entre lotes: 30s]")
                await page.wait_for_timeout(30000)

        await context.close()
        await browser.close()

    return total_coletados, total_salvos, total_duplicados, total_falhados


if __name__ == "__main__":
    inicio = time.perf_counter()
    coletados, salvos, duplicados, falhados = asyncio.run(executar())
    tempo_gasto = time.perf_counter() - inicio

    print("\n" + "=" * 50)
    print(f"TOTAL COLETADO:  {coletados} anúncios ({TOTAL_PAGINAS} páginas/lote | máx {MAX_LOTES} lotes)")
    print(f"SALVOS NO BANCO: {salvos}")
    print(f"DUPLICADOS:      {duplicados}")
    print(f"FALHADOS:        {falhados}")
    print(f"TEMPO GASTO:     {tempo_gasto:.2f} segundos")
    print("=" * 50)
