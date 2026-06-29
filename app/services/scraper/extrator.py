import re
from app.services.scraper.config import (
    SELETOR_LINK,
    SELETOR_TITULO,
    SELETOR_PRECO,
    SELETOR_LOCALIZACAO,
    SELETOR_QUILOMETRAGEM,
)


async def extrair_anuncio(card):
    link_element = card.locator(SELETOR_LINK)
    titulo = await link_element.locator(SELETOR_TITULO).inner_text()
    link = await link_element.get_attribute("href")
    preco_texto = await card.locator(SELETOR_PRECO).inner_text()
    preco = float(preco_texto.replace("R$", "").replace(".", "").strip())
    localizacao = await card.locator(SELETOR_LOCALIZACAO).inner_text()
    cidade = localizacao.split(",")[0].strip()
    quilometragem = await extrair_quilometragem(card)

    return {
        "titulo": titulo,
        "preco": preco,
        "cidade": cidade,
        "quilometragem": quilometragem,
        "link": link,
    }


async def extrair_quilometragem(card):
    km_locator = card.locator(SELETOR_QUILOMETRAGEM)
    if await km_locator.count() == 0:
        return None

    texto = await km_locator.inner_text()
    numeros = re.sub(r"[^\d]", "", texto)
    return int(numeros) if numeros else None
