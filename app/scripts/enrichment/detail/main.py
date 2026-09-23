import asyncio
import logging
import time

logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

from curl_cffi.requests import AsyncSession

from app.core.database import engine
engine.echo = False

from app.scripts.enrichment.detail.fetcher import MAX_CONCORRENCIA, extrair_datalayer_url
from app.scripts.enrichment.detail.parser import mapear_campos
from app.scripts.enrichment.detail.repositorio import BATCH_SIZE, atualizar_detalhes, buscar_para_enriquecer

INTERVALO_ESPERA = 30        # segundos entre verificações quando não há registros
MAX_ESPERA_SEGUNDOS = 600    # 10 minutos máximo esperando pelo próximo lote
SENTINEL_ERRO = "ERRO"


async def processar_carro(session, semaforo, carro) -> tuple[int, dict]:
    ad_detail = await extrair_datalayer_url(session, semaforo, carro.url_anuncio)

    if not ad_detail:
        print(f"  [FALHA] id={carro.id} → {carro.url_anuncio}")
        return (carro.id, {"marca": SENTINEL_ERRO})

    campos = mapear_campos(ad_detail)
    if not campos.get("marca"):
        campos["marca"] = SENTINEL_ERRO

    print(
        f"  [OK] id={carro.id} | {campos.get('marca', '?')} {campos.get('modelo', '?')} "
        f"{campos.get('ano', '?')} | câmbio={campos.get('cambio')} | cor={campos.get('cor', '?')}"
    )
    return (carro.id, campos)


async def aguardar_proximo_lote(current_min_id: int) -> list:
    """Espera até 10 minutos verificando a cada 30s. Retorna carros ou lista vazia."""
    max_tentativas = MAX_ESPERA_SEGUNDOS // INTERVALO_ESPERA
    for tentativa in range(1, max_tentativas + 1):
        print(f"  Aguardando novos registros... ({tentativa}/{max_tentativas}) — {INTERVALO_ESPERA}s")
        await asyncio.sleep(INTERVALO_ESPERA)
        carros = await buscar_para_enriquecer(current_min_id)
        if carros:
            return carros
    return []


async def executar():
    total_atualizados = 0
    total_erros = 0
    lote = 1
    current_min_id = 0

    semaforo = asyncio.Semaphore(MAX_CONCORRENCIA)

    async with AsyncSession() as session:
        while True:
            carros = await buscar_para_enriquecer(current_min_id)

            if not carros:
                print(f"\nNenhum registro com id > {current_min_id}. Aguardando scraper...")
                carros = await aguardar_proximo_lote(current_min_id)

                if not carros:
                    # Tenta pular um lote adiante
                    proximo_min_id = current_min_id + BATCH_SIZE
                    print(f"\nAinda sem registros. Pulando para id > {proximo_min_id}...")
                    carros = await buscar_para_enriquecer(proximo_min_id)

                    if not carros:
                        print("\nNenhum registro encontrado. Scraping finalizado. Encerrando.")
                        break

                    current_min_id = proximo_min_id

            print(f"\n{'=' * 50}")
            print(f"Lote {lote} | ids {carros[0].id}–{carros[-1].id} | {len(carros)} registros")
            print(f"{'=' * 50}")

            tasks = [processar_carro(session, semaforo, c) for c in carros]
            resultados = await asyncio.gather(*tasks)

            erros_lote = sum(1 for _, campos in resultados if campos.get("marca") == SENTINEL_ERRO)
            total_erros += erros_lote

            atualizados = await atualizar_detalhes(resultados)
            total_atualizados += atualizados

            current_min_id = carros[-1].id

            print(f"\nLote {lote} → processados: {atualizados} | erros: {erros_lote} | posição: id={current_min_id}")
            print(f"Acumulado → {total_atualizados} processados | {total_erros} erros")

            lote += 1

    return total_atualizados, total_erros


if __name__ == "__main__":
    inicio = time.perf_counter()
    atualizados, erros = asyncio.run(executar())
    tempo = time.perf_counter() - inicio

    print("\n" + "=" * 50)
    print(f"PROCESSADOS: {atualizados}")
    print(f"ERROS:       {erros}")
    print(f"TEMPO:       {tempo:.2f}s")
    print("=" * 50)
