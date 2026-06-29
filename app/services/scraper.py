import asyncio
from playwright.async_api import async_playwright

URL = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-mg?sp=2"
SELETOR_TITULO = 'a[data-testid="adcard-link"] h2'


async def pegar_primeiro_titulo():
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
        await page.goto(URL, timeout=60000)

        print("[4/5] Aguardando os anúncios carregarem...")
        await page.wait_for_selector(SELETOR_TITULO, timeout=15000)

        titulo = await page.locator(SELETOR_TITULO).first.inner_text()
        print(f"[5/5] Título encontrado: {titulo}")

        print("Fechando navegador em 3 segundos...")
        await page.wait_for_timeout(3000)
        await browser.close()

        return titulo


if __name__ == "__main__":
    resultado = asyncio.run(pegar_primeiro_titulo())
    print("=" * 50)
    print(f"RESULTADO FINAL: {resultado}")
    print("=" * 50)
