import asyncio
import json
import random

from curl_cffi.requests import AsyncSession

MAX_CONCORRENCIA = 5
DELAY_ENTRE_REQUESTS = (1, 3)

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Referer": "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios",
}


def _extrair_addetail_html(html: str) -> dict | None:
    """Extrai o JSON adDetail embutido no HTML (SSR) contando chaves."""
    idx = html.find('"adDetail":')
    if idx == -1:
        return None
    start = html.find('{', idx)
    if start == -1:
        return None
    depth = 0
    for i, char in enumerate(html[start:], start):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(html[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


async def extrair_datalayer_url(session: AsyncSession, semaforo: asyncio.Semaphore, url: str) -> dict | None:
    async with semaforo:
        try:
            response = await session.get(
                url,
                impersonate="chrome120",
                timeout=15,
                headers=HEADERS,
            )
            if response.status_code != 200:
                return None
            ad_detail = _extrair_addetail_html(response.text)
            if ad_detail:
                await asyncio.sleep(random.uniform(*DELAY_ENTRE_REQUESTS))
            return ad_detail
        except Exception as e:
            print(f"  [ERRO] {url}: {e}")
            return None
