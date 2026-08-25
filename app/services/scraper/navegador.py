from playwright.async_api import async_playwright
from app.services.scraper.config import URL_BASE, TOTAL_PAGINAS, SELETOR_CARD, SELETOR_PRECO, STEALTH_SCRIPT
from app.services.scraper.extrator import extrair_anuncio


def url_pagina(pagina: int) -> str:
    if pagina == 1:
        return URL_BASE
    return f"{URL_BASE}&o={pagina}"


async def extrair_pagina(page, pagina: int) -> list:
    url = url_pagina(pagina)
    print(f"\n--- Página {pagina}/{TOTAL_PAGINAS} | {url}")

    await page.goto(url, timeout=60000, wait_until="domcontentloaded")
    await page.wait_for_selector(SELETOR_CARD, timeout=30000)

    cards = page.locator(SELETOR_CARD)
    total = await cards.count()
    print(f"  {total} anúncios encontrados. Extraindo...")

    intervalo_scroll = 10
    anuncios = []
    falhados = 0
    for i in range(total):
        card = cards.nth(i)
        try:
            if i % intervalo_scroll == 0:
                try:
                    await card.scroll_into_view_if_needed()
                    await page.wait_for_timeout(random.randint(300, 600))
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
    print(f"Iniciando scraper | {TOTAL_PAGINAS} página(s)")
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
        for pagina in range(1, TOTAL_PAGINAS + 1):
            anuncios, falhados = await extrair_pagina(page, pagina)
            todos_anuncios.extend(anuncios)
            total_falhados += falhados

            if pagina < TOTAL_PAGINAS:
                if pagina % 3 == 0:
                    print(f"  [pausa longa: 10s]")
                    await page.wait_for_timeout(10000)
                else:
                    print(f"  [pausa: 1s]")
                    await page.wait_for_timeout(1000)

        await context.close()
        await browser.close()
        return todos_anuncios, total_falhados
