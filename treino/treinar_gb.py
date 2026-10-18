import time
from pathlib import Path
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from preparar_dados import preparar

print("Preparando dados...")
X_treino, X_teste, y_treino, y_teste, encoder = preparar()

print("\nConfigurações do modelo:")
print(f"  n_estimators : 30000")
print(f"  learning_rate: 0.01")
print(f"  max_depth    : 7")

print("\nTreinando Gradient Boosting...")
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
joblib.dump(modelo, DIR / "gb_modelo.pkl")
joblib.dump(encoder, DIR / "gb_encoder.pkl")
print(f"\nModelo salvo em {DIR / 'gb_modelo.pkl'}")
print(f"Encoder salvo em {DIR / 'gb_encoder.pkl'}")
