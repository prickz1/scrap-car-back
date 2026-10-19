from pathlib import Path

import joblib
import pandas as pd

FEATURES_NUMERICAS = ["idade_veiculo", "quilometragem"]
FEATURES_CATEGORICAS = ["marca", "modelo", "combustivel", "cambio", "cor", "tipo_veiculo", "direcao"]
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS

MARCAS_POPULARES = {
    "Fiat", "VW", "Volkswagen", "Chevrolet", "Ford",
    "Hyundai", "Renault", "Toyota", "Honda", "Jeep",
}

_modelo_geral = None
_encoder_geral = None
_modelo_popular = None
_encoder_popular = None


def carregar(models_dir: Path) -> None:
    global _modelo_geral, _encoder_geral, _modelo_popular, _encoder_popular
    _modelo_geral = joblib.load(models_dir / "gb_modelo.pkl")
    _encoder_geral = joblib.load(models_dir / "gb_encoder.pkl")

    popular_path = models_dir / "gb_modelo_popular.pkl"
    if popular_path.exists():
        _modelo_popular = joblib.load(popular_path)
        _encoder_popular = joblib.load(models_dir / "gb_encoder_popular.pkl")


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


def prever(df: pd.DataFrame) -> dict[str, pd.Series]:
    result = {"geral": _prever_com(df, _modelo_geral, _encoder_geral)}
    if _modelo_popular is not None:
        result["popular"] = _prever_com(df, _modelo_popular, _encoder_popular)
    return result
