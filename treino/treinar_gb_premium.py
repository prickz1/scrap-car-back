import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder

from database import carregar_dados

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
LIMITE_PREMIUM = 200_000

IDS_IGNORAR = [79641, 159336, 794481, 79645, 76207, 76183, 79626, 79521,
               79214, 79623, 79627, 79497, 79646, 79628, 79630, 71351,
               64802, 79624, 79629, 79351, 79631, 79659]

FEATURES_NUMERICAS   = ["idade_veiculo", "quilometragem"]
FEATURES_CATEGORICAS = ["marca", "modelo", "combustivel", "cambio", "cor", "tipo_veiculo", "direcao"]
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS

# ---------------------------------------------------------------------------
print("=" * 60)
print("REGRESSOR FAIXA PREMIUM — GradientBoostingRegressor")
print(f"Filtro: preço ≥ R$ {LIMITE_PREMIUM:,}")
print("=" * 60)

print("\n[1/4] Carregando dados do banco...")
df = carregar_dados()
df = df[~df["id"].isin(IDS_IGNORAR)]
df["idade_veiculo"] = 2026 - df["ano"]

s_km = df["quilometragem"].dropna()
lim_km = s_km.quantile(0.75) + 1.5 * (s_km.quantile(0.75) - s_km.quantile(0.25))
df = df[df["quilometragem"].isna() | (df["quilometragem"] <= lim_km)]
df = df.dropna(subset=FEATURES + ["preco"])

df = df[df["preco"] >= LIMITE_PREMIUM]

# IQR no preço para remover exóticos com precificação fora da curva
q1 = df["preco"].quantile(0.25)
q3 = df["preco"].quantile(0.75)
lim_preco = q3 + 1.5 * (q3 - q1)
df = df[df["preco"] <= lim_preco]

print(f"Total após filtros: {len(df):,} registros")
print(f"Preço  — min: R$ {df['preco'].min():,.0f} | max: R$ {df['preco'].max():,.0f} | média: R$ {df['preco'].mean():,.0f}")
print(f"Limite IQR aplicado: R$ {lim_preco:,.0f}")

# ---------------------------------------------------------------------------
print("\n[2/4] Preparando features e encoder...")
encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
df[FEATURES_CATEGORICAS] = encoder.fit_transform(df[FEATURES_CATEGORICAS])

X = df[FEATURES]
y = df["preco"]

X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Treino: {len(X_treino):,} | Teste: {len(X_teste):,}")

# ---------------------------------------------------------------------------
print("\n[3/4] Treinando GradientBoostingRegressor...")
print("  n_estimators : 30000")
print("  learning_rate: 0.01")
print("  max_depth    : 5  (reduzido para evitar overfitting no dataset menor)")

inicio = time.time()
modelo = GradientBoostingRegressor(
    n_estimators=30000, learning_rate=0.01, max_depth=5,
    random_state=42, verbose=1,
)
modelo.fit(X_treino, y_treino)
duracao = time.time() - inicio
print(f"\nTreino concluído em {duracao:.1f}s ({duracao/60:.1f} min)")

# ---------------------------------------------------------------------------
print("\n[4/4] Avaliando...")
y_pred = modelo.predict(X_teste)
mae  = mean_absolute_error(y_teste, y_pred)
rmse = np.sqrt(mean_squared_error(y_teste, y_pred))
r2   = r2_score(y_teste, y_pred)

print("\n" + "=" * 60)
print("RESULTADOS")
print("=" * 60)
print(f"\n  MAE:  R$ {mae:,.0f}")
print(f"  RMSE: R$ {rmse:,.0f}")
print(f"  R²:   {r2:.4f}")

print("\nFeature importance:")
for feat, imp in sorted(zip(modelo.feature_names_in_, modelo.feature_importances_), key=lambda x: -x[1]):
    print(f"  {feat:<20} {imp:.4f}")

# ---------------------------------------------------------------------------
DIR = Path(__file__).parent.parent / "modelos"
DIR.mkdir(exist_ok=True)
joblib.dump(modelo, DIR / "gb_faixa_premium.pkl")
joblib.dump(encoder, DIR / "gb_faixa_premium_encoder.pkl")

print(f"\nModelo salvo em {DIR / 'gb_faixa_premium.pkl'}")
print(f"Encoder salvo em {DIR / 'gb_faixa_premium_encoder.pkl'}")
print("=" * 60)
