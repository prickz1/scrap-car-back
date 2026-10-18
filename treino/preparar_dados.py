import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import train_test_split

from database import carregar_dados

IDS_IGNORAR = [79641, 159336, 794481, 79645, 76207, 76183, 79626, 79521,
               79214, 79623, 79627, 79497, 79646, 79628, 79630, 71351,
               64802, 79624, 79629, 79351, 79631, 79659]

FEATURES_NUMERICAS = ["idade_veiculo", "quilometragem"]
FEATURES_CATEGORICAS = ["marca", "modelo", "combustivel", "cambio", "cor", "tipo_veiculo", "direcao"]
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS
TARGET = "preco"


def _filtrar_outliers(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    s = df[coluna].dropna()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    limite = q3 + 1.5 * (q3 - q1)
    return df[df[coluna] <= limite]


def preparar(test_size: float = 0.2, random_state: int = 42):
    df = carregar_dados()

    df = df[~df["id"].isin(IDS_IGNORAR)]
    df["idade_veiculo"] = 2026 - df["ano"]
    df = _filtrar_outliers(df, "quilometragem")
    df = df.dropna(subset=FEATURES + [TARGET])

    encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    df[FEATURES_CATEGORICAS] = encoder.fit_transform(df[FEATURES_CATEGORICAS])

    X = df[FEATURES]
    y = df[TARGET]

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    print(f"Total após filtros: {len(df):,} registros")
    print(f"Treino: {len(X_treino):,} | Teste: {len(X_teste):,}")

    return X_treino, X_teste, y_treino, y_teste, encoder
