from pathlib import Path

import joblib
import pandas as pd

FEATURES_NUMERICAS = ["idade_veiculo", "quilometragem"]
FEATURES_CATEGORICAS = ["marca", "modelo", "combustivel", "cambio", "cor", "tipo_veiculo", "direcao"]
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS

_modelo = None
_encoder = None


def carregar(models_dir: Path) -> None:
    global _modelo, _encoder
    _modelo = joblib.load(models_dir / "gb_modelo.pkl")
    _encoder = joblib.load(models_dir / "gb_encoder.pkl")


def prever(df: pd.DataFrame) -> pd.Series:
    validos = df[FEATURES].notna().all(axis=1)
    enc = df[validos].copy()
    for col in FEATURES_CATEGORICAS:
        enc[col] = enc[col].fillna("Desconhecido")
    enc[FEATURES_CATEGORICAS] = _encoder.transform(enc[FEATURES_CATEGORICAS])
    result = pd.Series(index=df.index, dtype=float)
    if validos.any():
        result[validos] = _modelo.predict(enc[FEATURES])
    return result
