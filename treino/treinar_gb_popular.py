import time
from pathlib import Path
import numpy as np
import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder

from database import carregar_dados

MARCAS_POPULARES = [
    "Fiat", "VW", "Volkswagen", "Chevrolet", "Ford",
    "Hyundai", "Renault", "Toyota", "Honda", "Jeep",
]

IDS_IGNORAR = [79641, 159336, 794481, 79645, 76207, 76183, 79626, 79521,
               79214, 79623, 79627, 79497, 79646, 79628, 79630, 71351,
               64802, 79624, 79629, 79351, 79631, 79659]

FEATURES_NUMERICAS = ["idade_veiculo", "quilometragem"]
FEATURES_CATEGORICAS = ["marca", "modelo", "combustivel", "cambio", "cor", "tipo_veiculo", "direcao"]
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS
TARGET = "preco"


def _filtrar_outliers_km(df: pd.DataFrame) -> pd.DataFrame:
    s = df["quilometragem"].dropna()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    limite = q3 + 1.5 * (q3 - q1)
    return df[df["quilometragem"].isna() | (df["quilometragem"] <= limite)]


def _filtrar_outliers_preco_por_marca(df: pd.DataFrame) -> pd.DataFrame:
    q1 = df.groupby("marca")[TARGET].quantile(0.25).rename("q1")
    q3 = df.groupby("marca")[TARGET].quantile(0.75).rename("q3")
    limites = (q3 + 1.5 * (q3 - q1)).rename("limite")
    df = df.merge(limites, on="marca")
    df = df[df[TARGET] <= df["limite"]].drop(columns=["limite"])
    return df.reset_index(drop=True)


def preparar():
    df = carregar_dados()

    df = df[~df["id"].isin(IDS_IGNORAR)]
    print(f"Marcas únicas no banco: {sorted(df['marca'].dropna().unique().tolist())}")
    df = df[df["marca"].isin(MARCAS_POPULARES)]
    print(f"Após filtro de marcas populares: {len(df):,} registros")
    df["idade_veiculo"] = 2026 - df["ano"]
    df = _filtrar_outliers_km(df)
    print(f"Após filtro de km: {len(df):,} registros")
    df = _filtrar_outliers_preco_por_marca(df)
    print(f"Após filtro de preço por marca: {len(df):,} registros")
    df = df.dropna(subset=FEATURES + [TARGET])
    print(f"Após dropna: {len(df):,} registros")

    encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    df[FEATURES_CATEGORICAS] = encoder.fit_transform(df[FEATURES_CATEGORICAS])

    X = df[FEATURES]
    y = df[TARGET]

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Marcas incluídas: {', '.join(MARCAS_POPULARES)}")
    print(f"Total após filtros: {len(df):,} registros")
    print(f"Treino: {len(X_treino):,} | Teste: {len(X_teste):,}")

    return X_treino, X_teste, y_treino, y_teste, encoder


print("Preparando dados (carros populares)...")
X_treino, X_teste, y_treino, y_teste, encoder = preparar()

print("\nConfigurações do modelo:")
print(f"  n_estimators : 30000")
print(f"  learning_rate: 0.01")
print(f"  max_depth    : 7")

print("\nTreinando Gradient Boosting (popular)...")
inicio = time.time()

modelo = GradientBoostingRegressor(
    n_estimators=30000, learning_rate=0.01, max_depth=7,
    random_state=42, verbose=1,
)
modelo.fit(X_treino, y_treino)

duracao = time.time() - inicio
print(f"\nTreino concluído em {duracao/60:.1f} min")

print("\nAvaliando...")
y_pred = modelo.predict(X_teste)
mae  = mean_absolute_error(y_teste, y_pred)
rmse = np.sqrt(mean_squared_error(y_teste, y_pred))
r2   = r2_score(y_teste, y_pred)

print(f"\nResultados:")
print(f"  MAE:  R$ {mae:,.0f}")
print(f"  RMSE: R$ {rmse:,.0f}")
print(f"  R²:   {r2:.4f}")

print("\nFeature importance:")
for feat, imp in sorted(zip(modelo.feature_names_in_, modelo.feature_importances_), key=lambda x: -x[1]):
    print(f"  {feat:<20} {imp:.4f}")

DIR = Path(__file__).parent.parent / "modelos"
DIR.mkdir(exist_ok=True)
joblib.dump(modelo, DIR / "gb_modelo_popular.pkl")
joblib.dump(encoder, DIR / "gb_encoder_popular.pkl")
print(f"\nModelo salvo em {DIR / 'gb_modelo_popular.pkl'}")
print(f"Encoder salvo em {DIR / 'gb_encoder_popular.pkl'}")
