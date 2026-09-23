import re


def extrair_marca(titulo: str | None) -> str | None:
    """Extrai a marca do título (primeira palavra antes de espaço, hífen ou barra)."""
    if not titulo:
        return None
    partes = re.split(r"[ \-/]", titulo.strip(), maxsplit=1)
    return partes[0] if partes else None


def extrair_ano(titulo: str | None) -> int | None:
    """Extrai o ano do título (primeiro 19xx ou 20xx encontrado em qualquer posição)."""
    if not titulo:
        return None
    match = re.search(r"\b(19\d{2}|20[0-3]\d)\b", titulo)
    return int(match.group(1)) if match else None


def extrair_modelo(titulo: str | None, marca: str | None) -> str | None:
    """Extrai o modelo do título (entre a marca e a motorização ou o ano)."""
    if not titulo or not marca:
        return None
    sem_marca = re.sub(rf"^{re.escape(marca)}\s*", "", titulo.strip(), flags=re.IGNORECASE)
    # Tenta parar na motorização (ex: 1.4, 2.0)
    match = re.match(r"^(.+?)\s+\d+\.\d+", sem_marca)
    if match:
        return match.group(1).strip()
    # Fallback: tenta parar no ano (1900-2039)
    match = re.match(r"^(.+?)\s+(19\d{2}|20[0-3]\d)\b", sem_marca)
    return match.group(1).strip() if match else None
