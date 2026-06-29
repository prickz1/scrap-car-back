from playwright.async_api import async_playwright
from app.services.scraper.config import URL, SELETOR_CARD
from app.services.scraper.extrator import extrair_anuncio


async def pegar_anuncios():
    print("=" * 50)
    print("Iniciando scraper...")
    print(f"URL: {URL}")
    print("=" * 50)

    async with async_playwright() as p:
        print("[1/5] Abrindo navegador...")
        browser = await p.chromium.launch(headless=True)

        print("[2/5] Criando nova aba...")
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        )

        print("[3/5] Navegando até a página da OLX...")
        await page.goto(URL, timeout=60000, wait_until="domcontentloaded")

        print("[4/5] Aguardando os anúncios carregarem...")
        await page.wait_for_selector(SELETOR_CARD, timeout=15000)

        cards = page.locator(SELETOR_CARD)
        total = await cards.count()
        print(f"[5/5] {total} anúncios encontrados. Extraindo...")

        anuncios = []
        for i in range(total):
            card = cards.nth(i)
            try:
                anuncio = await extrair_anuncio(card)
                anuncios.append(anuncio)
                print(f"  [{i + 1}/{total}] {anuncio['titulo']} - R$ {anuncio['preco']} - {anuncio['quilometragem']} km")
            except Exception as erro:
                print(f"  [{i + 1}/{total}] Falhou ao extrair: {erro}")

        await browser.close()
        return anuncios
