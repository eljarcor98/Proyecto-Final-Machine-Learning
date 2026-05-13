import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
import joblib

def train_and_compare():
    # 1. Cargar datos
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'daily_ml_dataset.csv')
    if not os.path.exists(data_path):
        print("Error: No se encuentra el dataset. Ejecuta primero src/features.py")
        return

    df = pd.read_sql_query if False else pd.read_csv(data_path) # Mock read
    
    # 2. Definir Features (X) y Target (y)
    features = ['total_articles', 'pct_conflict', 'pct_economy', 'mentions_israel', 'mentions_iran']
    X = df[features]
    y = df['target_alert']
    
    print(f"Entrenando con {len(df)} muestras y {len(features)} características.")
    
    # 3. Dividir Train/Test
    # Debido a que tenemos pocos días, usaremos un test_size pequeño o simplemente entrenaremos para demostrar el flujo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 4. Definir Modelos
    models = {
        "Naive Bayes": GaussianNB(),
        "Logistic Regression": LogisticRegression(),
        "KNN (k=3)": KNeighborsClassifier(n_neighbors=3)
    }
    
    results = []
    
    os.makedirs('models', exist_ok=True)
    
    print("\n--- Resultados de Comparación de Modelos ---")
    for name, model in models.items():
        # Entrenar
        model.fit(X_train, y_train)
        
        # Predecir
        y_pred = model.predict(X_test)
        
        # Evaluar
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        print(f"{name}: Accuracy = {acc:.2f}, F1-Score = {f1:.2f}")
        
        results.append({
            "Model": name,
            "Accuracy": acc,
            "F1-Score": f1
        })
        
        # Guardar modelo
        model_name = name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("=", "")
        joblib.dump(model, f'models/{model_name}.pkl')
    
    # 5. Guardar resumen de resultados
    results_df = pd.DataFrame(results)
    results_df.to_csv('models/model_comparison.csv', index=False)
    print("\nModelos guardados en la carpeta /models/")

if __name__ == "__main__":
    train_and_compare()
