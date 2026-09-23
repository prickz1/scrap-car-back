from app.services.scraper.config import URL_BASE, TOTAL_PAGINAS, SELETOR_CARD, STEALTH_SCRIPT
from app.services.scraper.extrator import extrair_anuncio

MAX_TENTATIVAS = 3
ESPERA_RETRY = 15000


def url_pagina(preco_minimo, pagina: int) -> str:
    if preco_minimo is not None:
        base = f"{URL_BASE}&ps={int(preco_minimo)}"
    else:
        base = URL_BASE
    if pagina == 1:
        return base
    return f"{base}&o={pagina}"


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



async def criar_contexto(playwright):
    browser = await playwright.chromium.launch(
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
    return browser, context, page
