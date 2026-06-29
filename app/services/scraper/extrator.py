from app.services.scraper.config import (
    SELETOR_LINK,
    SELETOR_TITULO,
    SELETOR_PRECO,
    SELETOR_LOCALIZACAO,
)


async def extrair_anuncio(card):
    link_element = card.locator(SELETOR_LINK)
    titulo = await link_element.locator(SELETOR_TITULO).inner_text()
    link = await link_element.get_attribute("href")
    preco_texto = await card.locator(SELETOR_PRECO).inner_text()
    preco = float(preco_texto.replace("R$", "").replace(".", "").strip())
    localizacao = await card.locator(SELETOR_LOCALIZACAO).inner_text()
    cidade = localizacao.split(",")[0].strip()

    return {"titulo": titulo, "preco": preco, "cidade": cidade, "link": link}
