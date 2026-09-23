import re

# Mapeamento: chave no dataLayer → campo no banco
MAPA_CAMPOS = {
    "brand":        "marca",
    "model":        "modelo",
    "regdate":      "ano",
    "mileage":      "quilometragem",
    "fuel":         "combustivel",
    "gearbox":      "cambio",
    "carcolor":     "cor",
    "cartype":      "tipo_veiculo",
    "motorpower":   "potencia_motor",
    "car_steering": "direcao",
    "doors":        "portas",
}


def mapear_campos(ad_detail: dict) -> dict:
    resultado = {}
    for chave_olx, campo_db in MAPA_CAMPOS.items():
        valor = ad_detail.get(chave_olx)
        if not valor:
            continue
        if campo_db == "ano":
            try:
                resultado[campo_db] = int(valor)
            except (ValueError, TypeError):
                pass
        elif campo_db == "quilometragem":
            try:
                km = int(valor)
                if km <= 2147483647:
                    resultado[campo_db] = km
            except (ValueError, TypeError):
                pass
        elif campo_db == "portas":
            match = re.search(r"\d+", str(valor))
            if match:
                resultado[campo_db] = int(match.group())
        else:
            resultado[campo_db] = str(valor)
    return resultado
