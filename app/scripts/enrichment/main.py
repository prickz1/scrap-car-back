import asyncio
import time

from app.scripts.enrichment.extrator import extrair_ano, extrair_marca, extrair_modelo
from app.scripts.enrichment.repositorio import atualizar_enriquecimento, buscar_para_enriquecer


async def executar():
    total_atualizados = 0
    total_sem_titulo = 0
    lote = 1

    while True:
        carros = await buscar_para_enriquecer()
        if not carros:
            break

        print(f"Lote {lote} | {len(carros)} registros")

        registros = []
        for carro in carros:
            valores = {}

            if carro.marca is None:
                marca = extrair_marca(carro.titulo)
                if marca:
                    valores["marca"] = marca

            marca_atual = valores.get("marca") or carro.marca
            if carro.modelo is None:
                modelo = extrair_modelo(carro.titulo, marca_atual)
                if modelo:
                    valores["modelo"] = modelo

            if carro.ano is None:
                ano = extrair_ano(carro.titulo)
                if ano:
                    valores["ano"] = ano

            if valores:
                registros.append((carro.id, valores))
            else:
                total_sem_titulo += 1
                print(f"  [AVISO] id={carro.id} nada extraído: {carro.titulo!r}")

        atualizados = await atualizar_enriquecimento(registros)
        total_atualizados += atualizados
        print(f"  Atualizados: {atualizados} | Sem extração: {total_sem_titulo}")

        if atualizados == 0:
            print(f"  [AVISO] Lote sem nenhuma atualização — possível loop detectado. Encerrando.")
            break

        lote += 1

    return total_atualizados, total_sem_titulo


if __name__ == "__main__":
    inicio = time.perf_counter()
    atualizados, sem_extracao = asyncio.run(executar())
    tempo = time.perf_counter() - inicio

    print("\n" + "=" * 50)
    print(f"REGISTROS ATUALIZADOS: {atualizados}")
    print(f"SEM EXTRAÇÃO:          {sem_extracao}")
    print(f"TEMPO GASTO:           {tempo:.2f}s")
    print("=" * 50)
