from playwright.async_api import async_playwright
from app.services.scraper.config import URL_BASE, TOTAL_PAGINAS, MAX_LOTES, SELETOR_CARD, STEALTH_SCRIPT
from app.services.scraper.extrator import extrair_anuncio


def url_pagina(preco_minimo, pagina: int) -> str:
    if preco_minimo is not None:
        base = f"{URL_BASE}&ps={int(preco_minimo)}"
    else:
        base = URL_BASE
    if pagina == 1:
        return base
    return f"{base}&o={pagina}"


MAX_TENTATIVAS = 3
ESPERA_RETRY = 15000


async def extrair_pagina(page, preco_minimo, pagina: int) -> tuple:
    url = url_pagina(preco_minimo, pagina)
    print(f"\n--- Página {pagina}/{TOTAL_PAGINAS} | {url}")

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_selector(SELETOR_CARD, timeout=30000)
            break
        except Exception as e:
            if tentativa == MAX_TENTATIVAS:
                print(f"  [ERRO] Página {pagina} falhou após {MAX_TENTATIVAS} tentativas: {e}")
                return [], 0
            print(f"  [retry {tentativa}/{MAX_TENTATIVAS}] Aguardando {ESPERA_RETRY // 1000}s...")
            await page.wait_for_timeout(ESPERA_RETRY)

    cards = page.locator(SELETOR_CARD)
    total = await cards.count()
    print(f"  {total} anúncios encontrados. Extraindo...")

    anuncios = []
    falhados = 0
    for i in range(total):
        card = cards.nth(i)
        try:
            if i % 10 == 0:
                try:
                    await card.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)
                except Exception:
                    pass
            anuncio = await extrair_anuncio(card)
            anuncios.append(anuncio)
            print(f"  [{i + 1}/{total}] {anuncio['titulo']} - R$ {anuncio['preco']} - {anuncio['quilometragem']} km")
        except Exception as erro:
            falhados += 1
            print(f"  [{i + 1}/{total}] Falhou ao extrair: {erro}")

    print(f"  Extraídos: {len(anuncios)} | Falhados: {falhados}")
    return anuncios, falhados


async def pegar_anuncios():
    print("=" * 50)
    print(f"Iniciando scraper | até {MAX_LOTES} lotes × {TOTAL_PAGINAS} páginas")
    print("=" * 50)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="pt-BR",
            extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9"},
        )
        await context.add_init_script(STEALTH_SCRIPT)
        page = await context.new_page()

        todos_anuncios = []
        total_falhados = 0
        preco_minimo = None

        for lote in range(1, MAX_LOTES + 1):
            print(f"\n{'=' * 50}")
            print(f"Lote {lote}/{MAX_LOTES} | ps={preco_minimo or 'sem filtro'}")
            print(f"{'=' * 50}")

            anuncios_lote = []
            falhados_lote = 0

            for pagina in range(1, TOTAL_PAGINAS + 1):
                anuncios, falhados = await extrair_pagina(page, preco_minimo, pagina)
                anuncios_lote.extend(anuncios)
                falhados_lote += falhados

                if pagina < TOTAL_PAGINAS:
                    await page.wait_for_timeout(1000)

            if not anuncios_lote:
                print("\nNenhum anúncio encontrado. Coleta finalizada.")
                break

            todos_anuncios.extend(anuncios_lote)
            total_falhados += falhados_lote

            ultimo_preco = anuncios_lote[-1]["preco"]
            print(f"\n  Último preço do lote: R$ {ultimo_preco}")

            if ultimo_preco == preco_minimo:
                print("  Sem progresso de preço. Coleta finalizada.")
                break

            preco_minimo = ultimo_preco

            if lote < MAX_LOTES:
                print(f"  [pausa entre lotes: 30s]")
                await page.wait_for_timeout(30000)

        await context.close()
        await browser.close()
        return todos_anuncios, total_falhados
