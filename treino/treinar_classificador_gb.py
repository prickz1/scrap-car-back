import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder

from database import carregar_dados

# ---------------------------------------------------------------------------
# Configuração das faixas de preço
# ---------------------------------------------------------------------------
FAIXAS = {0: "Econômico (<R$80k)", 1: "Médio (R$80k–200k)", 2: "Premium (>R$200k)"}
LIMITES = [80_000, 200_000]

IDS_IGNORAR = [79641, 159336, 794481, 79645, 76207, 76183, 79626, 79521,
               79214, 79623, 79627, 79497, 79646, 79628, 79630, 71351,
               64802, 79624, 79629, 79351, 79631, 79659]

FEATURES_NUMERICAS = ["idade_veiculo", "quilometragem"]
FEATURES_CATEGORICAS = ["marca", "modelo", "combustivel", "cambio", "cor", "tipo_veiculo", "direcao"]
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS


def classificar_faixa(preco: float) -> int:
    if preco < LIMITES[0]:
        return 0
    if preco < LIMITES[1]:
        return 1
    return 2


# ---------------------------------------------------------------------------
# Preparar dados
# ---------------------------------------------------------------------------
print("=" * 60)
print("CLASSIFICADOR DE FAIXA DE PREÇO — GradientBoostingClassifier")
print("=" * 60)

print("\n[1/4] Carregando dados do banco...")
df = carregar_dados()
df = df[~df["id"].isin(IDS_IGNORAR)]
df["idade_veiculo"] = 2026 - df["ano"]

s_km = df["quilometragem"].dropna()
lim_km = s_km.quantile(0.75) + 1.5 * (s_km.quantile(0.75) - s_km.quantile(0.25))
df = df[df["quilometragem"].isna() | (df["quilometragem"] <= lim_km)]
df = df.dropna(subset=FEATURES + ["preco"])

df["faixa"] = df["preco"].apply(classificar_faixa)

print(f"Total após filtros: {len(df):,} registros")
print("\nDistribuição das faixas:")
for faixa_id, label in FAIXAS.items():
    n = (df["faixa"] == faixa_id).sum()
    pct = n / len(df) * 100
    print(f"  {label}: {n:,} ({pct:.1f}%)")

# ---------------------------------------------------------------------------
# Encode e split
# ---------------------------------------------------------------------------
print("\n[2/4] Preparando features e encoder...")
encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
df[FEATURES_CATEGORICAS] = encoder.fit_transform(df[FEATURES_CATEGORICAS])

X = df[FEATURES]
y = df["faixa"]

X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Treino: {len(X_treino):,} | Teste: {len(X_teste):,}")

# ---------------------------------------------------------------------------
# Treino
# ---------------------------------------------------------------------------
print("\n[3/4] Treinando GradientBoostingClassifier...")
print("  n_estimators : 5000")
print("  learning_rate: 0.01")
print("  max_depth    : 5")

inicio = time.time()
modelo = GradientBoostingClassifier(
    n_estimators=5000, learning_rate=0.01, max_depth=5,
    random_state=42, verbose=1,
)
modelo.fit(X_treino, y_treino)
duracao = time.time() - inicio
print(f"\nTreino concluído em {duracao:.1f}s ({duracao/60:.1f} min)")

# ---------------------------------------------------------------------------
# Avaliação
# ---------------------------------------------------------------------------
print("\n[4/4] Avaliando...")
y_pred = modelo.predict(X_teste)

acuracia = accuracy_score(y_teste, y_pred)

print("\n" + "=" * 60)
print("RESULTADOS")
print("=" * 60)
print(f"\nAcurácia geral: {acuracia:.4f} ({acuracia*100:.2f}%)")

print("\nRelatório por faixa:")
print(classification_report(y_teste, y_pred, target_names=list(FAIXAS.values())))

print("Matriz de confusão:")
cm = confusion_matrix(y_teste, y_pred)
header = f"{'':>25}" + "".join(f"{FAIXAS[i]:>22}" for i in range(3))
print(header)
for i, row in enumerate(cm):
    linha = f"  Real {FAIXAS[i]:>20}" + "".join(f"{v:>22,}" for v in row)
    print(linha)

print("\nFeature importance:")
for feat, imp in sorted(zip(modelo.feature_names_in_, modelo.feature_importances_), key=lambda x: -x[1]):
    print(f"  {feat:<20} {imp:.4f}")

# ---------------------------------------------------------------------------
# Salvar
# ---------------------------------------------------------------------------
DIR = Path(__file__).parent.parent / "modelos"
DIR.mkdir(exist_ok=True)
joblib.dump(modelo, DIR / "clf_faixa_gb.pkl")
joblib.dump(encoder, DIR / "clf_faixa_gb_encoder.pkl")

print(f"\nModelo salvo em {DIR / 'clf_faixa_gb.pkl'}")
print(f"Encoder salvo em {DIR / 'clf_faixa_gb_encoder.pkl'}")
print("=" * 60)
