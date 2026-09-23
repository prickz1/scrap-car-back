import re
from app.services.scraper.config import (
    SELETOR_LINK,
    SELETOR_TITULO,
    SELETOR_PRECO,
    SELETOR_LOCALIZACAO,
    SELETOR_QUILOMETRAGEM,
    KM_MAXIMO,
)


async def extrair_anuncio(card):
    link_element = card.locator(SELETOR_LINK)
    titulo = await link_element.locator(SELETOR_TITULO).inner_text()
    link = await link_element.get_attribute("href")
    preco_locator = card.locator(SELETOR_PRECO)
    count = await preco_locator.count()
    if count == 0:
        raise ValueError("sem elemento de preço")
    preco_texto = await preco_locator.inner_text()
    preco_limpo = preco_texto.replace("R$", "").replace(".", "").strip()
    if not preco_limpo:
        titulo_debug = await card.locator(SELETOR_TITULO).inner_text()
        raise ValueError(f"preço vazio | titulo={titulo_debug!r}")
    preco = float(preco_limpo)
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
    if not numeros:
        return None

    km = int(numeros)
    # anunciantes às vezes colocam valores absurdos (ex: 99999999999)
    return km if km <= KM_MAXIMO else None
