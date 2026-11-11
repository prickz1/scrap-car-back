from pathlib import Path

import joblib
import pandas as pd

FEATURES_NUMERICAS   = ["idade_veiculo", "quilometragem"]
FEATURES_CATEGORICAS = ["marca", "modelo", "combustivel", "cambio", "cor", "tipo_veiculo", "direcao"]
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS

MARCAS_POPULARES = {
    "Fiat", "VW", "Volkswagen", "Chevrolet", "Ford",
    "Hyundai", "Renault", "Toyota", "Honda", "Jeep",
}

FAIXA_LABELS = {0: "Econômico", 1: "Médio", 2: "Premium"}

# Modelos geral e popular
_modelo_geral    = None
_encoder_geral   = None
_modelo_popular  = None
_encoder_popular = None

# Classificador de faixa
_clf_faixa         = None
_clf_faixa_encoder = None

# Regressores especializados por faixa
_modelos_faixa  = {}   # {0: modelo_eco, 1: modelo_medio, 2: modelo_premium}
_encoders_faixa = {}   # {0: encoder_eco, ...}


def esta_carregado() -> bool:
    return _modelo_geral is not None


def carregar(models_dir: Path) -> None:
    global _modelo_geral, _encoder_geral
    global _modelo_popular, _encoder_popular
    global _clf_faixa, _clf_faixa_encoder
    global _modelos_faixa, _encoders_faixa

    _modelo_geral  = joblib.load(models_dir / "gb_modelo.pkl")
    _encoder_geral = joblib.load(models_dir / "gb_encoder.pkl")

    popular_path = models_dir / "gb_modelo_popular.pkl"
    if popular_path.exists():
        _modelo_popular  = joblib.load(popular_path)
        _encoder_popular = joblib.load(models_dir / "gb_encoder_popular.pkl")

    clf_path = models_dir / "clf_faixa_gb.pkl"
    if clf_path.exists():
        _clf_faixa         = joblib.load(clf_path)
        _clf_faixa_encoder = joblib.load(models_dir / "clf_faixa_gb_encoder.pkl")

        nomes = {0: "economico", 1: "medio", 2: "premium"}
        for idx, nome in nomes.items():
            reg_path = models_dir / f"gb_faixa_{nome}.pkl"
            if reg_path.exists():
                _modelos_faixa[idx]  = joblib.load(reg_path)
                _encoders_faixa[idx] = joblib.load(models_dir / f"gb_faixa_{nome}_encoder.pkl")


def _prever_com(df: pd.DataFrame, modelo, encoder) -> pd.Series:
    validos = df[FEATURES].notna().all(axis=1)
    enc = df[validos].copy()
    for col in FEATURES_CATEGORICAS:
        enc[col] = enc[col].fillna("Desconhecido")
    enc[FEATURES_CATEGORICAS] = encoder.transform(enc[FEATURES_CATEGORICAS])
    result = pd.Series(index=df.index, dtype=float)
    if validos.any():
        result[validos] = modelo.predict(enc[FEATURES])
    return result


def _prever_faixas(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Classifica a faixa e usa o regressor especializado de cada faixa."""
    precos = pd.Series(index=df.index, dtype=float)
    faixas = pd.Series(index=df.index, dtype=str)

    validos = df[FEATURES].notna().all(axis=1)
    if not validos.any():
        return {"preco": precos, "faixa": faixas}

    enc = df[validos].copy()
    for col in FEATURES_CATEGORICAS:
        enc[col] = enc[col].fillna("Desconhecido")
    enc[FEATURES_CATEGORICAS] = _clf_faixa_encoder.transform(enc[FEATURES_CATEGORICAS])

    faixas_pred = _clf_faixa.predict(enc[FEATURES])

    for idx_faixa, label in FAIXA_LABELS.items():
        mask = faixas_pred == idx_faixa
        if not mask.any():
            continue
        if idx_faixa not in _modelos_faixa:
            continue

        rows = df[validos][mask]
        preco_pred = _prever_com(rows, _modelos_faixa[idx_faixa], _encoders_faixa[idx_faixa])
        precos[rows.index] = preco_pred
        faixas[rows.index] = label

    return {"preco": precos, "faixa": faixas}


def prever(df: pd.DataFrame) -> dict:
    result = {"geral": _prever_com(df, _modelo_geral, _encoder_geral)}

    if _modelo_popular is not None:
        result["popular"] = _prever_com(df, _modelo_popular, _encoder_popular)

    if _clf_faixa is not None and _modelos_faixa:
        result["faixas"] = _prever_faixas(df)

    return result
