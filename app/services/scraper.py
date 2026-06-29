import asyncio
from playwright.async_api import async_playwright

URL = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-mg?sp=2"
SELETOR_CARD = 'div.olx-adcard__content'
SELETOR_LINK = 'a[data-testid="adcard-link"]'
SELETOR_TITULO = 'h2'
SELETOR_PRECO = 'h3.olx-adcard__price'
SELETOR_LOCALIZACAO = 'p.olx-adcard__location'


async def pegar_primeiro_anuncio():
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

        card = page.locator(SELETOR_CARD).first
        link_element = card.locator(SELETOR_LINK)
        titulo = await link_element.locator(SELETOR_TITULO).inner_text()
        link = await link_element.get_attribute("href")
        preco_texto = await card.locator(SELETOR_PRECO).inner_text()
        preco = float(preco_texto.replace("R$", "").replace(".", "").strip())
        localizacao = await card.locator(SELETOR_LOCALIZACAO).inner_text()
        cidade = localizacao.split(",")[0].strip()

        print(f"[5/5] Título encontrado: {titulo}")
        print(f"       Preço: {preco}")
        print(f"       Cidade: {cidade}")
        print(f"       Link: {link}")

        print("Fechando navegador em 3 segundos...")
        await page.wait_for_timeout(3000)
        await browser.close()

        return {"titulo": titulo, "preco": preco, "cidade": cidade, "link": link}


if __name__ == "__main__":
    resultado = asyncio.run(pegar_primeiro_anuncio())
    print("=" * 50)
    print(f"RESULTADO FINAL: {resultado}")
    print("=" * 50)
