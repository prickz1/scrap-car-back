import asyncio
import time
from app.services.scraper.navegador import pegar_anuncios


if __name__ == "__main__":
    inicio = time.perf_counter()
    resultado = asyncio.run(pegar_anuncios())
    tempo_gasto = time.perf_counter() - inicio

    print("=" * 50)
    print(f"TOTAL COLETADO: {len(resultado)} anúncios")
    print(f"TEMPO GASTO: {tempo_gasto:.2f} segundos")
    print("=" * 50)
