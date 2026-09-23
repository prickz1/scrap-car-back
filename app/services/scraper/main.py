import asyncio
import sys
import time
from playwright.async_api import async_playwright
from app.core.database import engine
from app.services.scraper.config import TOTAL_PAGINAS, MAX_LOTES
from app.services.scraper.navegador import criar_contexto, extrair_pagina
from app.services.scraper.persistencia import salvar_anuncios

engine.echo = False


async def executar(preco_inicial=None):
    total_salvos = 0
    total_duplicados = 0
    total_falhados = 0
    total_coletados = 0
    preco_minimo = preco_inicial

    async with async_playwright() as p:
        browser, context, page = await criar_contexto(p)

        for lote in range(1, MAX_LOTES + 1):
            print(f"\n{'=' * 50}")
            print(f"Lote {lote}/{MAX_LOTES} | ps={preco_minimo or 'sem filtro'}")
            print(f"{'=' * 50}")

            anuncios_lote = []
            falhados_lote = 0
            ultimo_preco_lote = preco_minimo

            for pagina in range(1, TOTAL_PAGINAS + 1):
                anuncios, falhados = await extrair_pagina(page, preco_minimo, pagina)
                falhados_lote += falhados

                if anuncios:
                    salvamento = await salvar_anuncios(anuncios)
                    total_coletados += len(anuncios)
                    total_salvos += salvamento["salvos"]
                    total_duplicados += salvamento["duplicados"]
                    anuncios_lote.extend(anuncios)
                    ultimo_preco_lote = anuncios[-1]["preco"]
                    print(f"  Página {pagina} salva → {salvamento['salvos']} salvos | {salvamento['duplicados']} duplicados")

                if pagina < TOTAL_PAGINAS:
                    await page.wait_for_timeout(1000)

            total_falhados += falhados_lote

            if not anuncios_lote:
                print("\nNenhum anúncio encontrado no lote. Encerrando coleta.")
                break

            print(f"\nLote {lote} concluído → acumulado: {total_salvos} salvos | {total_duplicados} duplicados")

            if ultimo_preco_lote == preco_minimo:
                print("Sem progresso de preço. Encerrando coleta.")
                break

            preco_minimo = ultimo_preco_lote

            if lote < MAX_LOTES:
                print(f"\n[pausa entre lotes: 30s]")
                await page.wait_for_timeout(30000)

        await context.close()
        await browser.close()

    return total_coletados, total_salvos, total_duplicados, total_falhados


if __name__ == "__main__":
    preco_inicial = int(sys.argv[1]) if len(sys.argv) > 1 else None
    inicio = time.perf_counter()
    coletados, salvos, duplicados, falhados = asyncio.run(executar(preco_inicial))
    tempo_gasto = time.perf_counter() - inicio

    print("\n" + "=" * 50)
    print(f"TOTAL COLETADO:  {coletados} anúncios ({TOTAL_PAGINAS} páginas/lote | máx {MAX_LOTES} lotes)")
    print(f"SALVOS NO BANCO: {salvos}")
    print(f"DUPLICADOS:      {duplicados}")
    print(f"FALHADOS:        {falhados}")
    print(f"TEMPO GASTO:     {tempo_gasto:.2f} segundos")
    print("=" * 50)
