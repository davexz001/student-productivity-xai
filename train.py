import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import shap

def run_training_pipeline():
    print("=== STEP 1: LOADING DATASET ===")
    data_path = "data/student-mat.csv"
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset missing! Ensure student-mat.csv is inside data/ folder.")

    df = pd.read_csv(data_path, sep=';')
    print(f"Dataset successfully loaded. Total records: {len(df)}")

    print("\n=== STEP 2: PREPROCESSING FEATURES (INCLUDING G1 & G2) ===")
    target_col = 'G3'

    # Map essential binary text columns to numbers
    binary_cols = ['schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic']
    for col in binary_cols:
        if col in df.columns:
            df[col] = df[col].map({'yes': 1, 'no': 0})

    # Select features including past exam scores (G1 & G2)
    feature_cols = [
        'G1', 'G2', 'studytime', 'failures', 'absences', 'health', 'goout', 
        'freetime', 'Dalc', 'Walc', 'famrel', 'Medu', 'Fedu',
        'schoolsup', 'famsup', 'higher', 'internet'
    ]

    selected_cols = [c for c in feature_cols if c in df.columns]
    
    X = df[selected_cols]
    y = df[target_col]

    os.makedirs("models", exist_ok=True)
    joblib.dump(selected_cols, "models/model_columns.pkl")

    print("\n=== STEP 3: SPLITTING DATA & TRAINING RANDOM FOREST MODEL ===")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf_model.fit(X_train, y_train)

    print("\n=== STEP 4: MODEL EVALUATION ===")
    predictions = rf_model.predict(X_test)
    r2 = r2_score(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    print(f"R² Score: {r2 * 100:.2f}%")
    print(f"MAE: {mae:.2f}")

    print("\n=== STEP 5: EXPORTING ARTIFACTS ===")
    joblib.dump(rf_model, "models/student_productivity_model.pkl")

    explainer = shap.TreeExplainer(rf_model)
    joblib.dump(explainer, "models/shap_explainer.pkl")
    print("All artifacts successfully updated in models/ directory!")

if __name__ == "__main__":
    run_training_pipeline()