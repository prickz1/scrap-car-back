from playwright.async_api import async_playwright
from app.services.scraper.config import URL, SELETOR_CARD, SELETOR_PRECO
from app.services.scraper.extrator import extrair_anuncio

STEALTH_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});
window.chrome = {runtime: {}, loadTimes: function(){}, csi: function(){}, app: {}};
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
    parameters.name === 'notifications'
        ? Promise.resolve({state: Notification.permission})
        : originalQuery(parameters);
"""


async def pegar_anuncios():
    print("=" * 50)
    print("Iniciando scraper...")
    print(f"URL: {URL}")
    print("=" * 50)

    async with async_playwright() as p:
        print("[1/5] Abrindo navegador...")
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )

        print("[2/5] Criando nova aba...")
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

        print("[3/5] Navegando até a página da OLX...")
        await page.goto(URL, timeout=60000, wait_until="domcontentloaded")

        html = await page.content()
        with open("/app/debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("[4/5] Aguardando os anúncios carregarem...")
        await page.wait_for_selector(SELETOR_CARD, timeout=30000)

        cards = page.locator(SELETOR_CARD)
        total = await cards.count()
        print(f"[5/5] {total} anúncios encontrados. Extraindo...")

        anuncios = []
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
                print(f"  [{i + 1}/{total}] Falhou ao extrair: {erro}")

        await context.close()
        await browser.close()
        return anuncios
