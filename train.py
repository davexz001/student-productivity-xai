import pandas as pd
import numpy as np
import joblib
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import os

print("=" * 60)
print("TRAINING STUDENT PRODUCTIVITY MODEL WITH G1 AND G2")
print("=" * 60)

# Load data
df = pd.read_csv('data/student-mat.csv', sep=';')
print(f"Loaded {len(df)} records")

# Features to use (including G1 and G2!)
features = [
    'studytime', 'failures', 'absences', 'health', 'goout',
    'freetime', 'Dalc', 'Walc', 'famrel', 'Medu', 'Fedu',
    'schoolsup', 'famsup', 'higher', 'internet',
    'G1', 'G2'  # ← G1 and G2 ADDED!
]

# Convert categorical to numeric
df['schoolsup'] = (df['schoolsup'] == 'yes').astype(int)
df['famsup'] = (df['famsup'] == 'yes').astype(int)
df['higher'] = (df['higher'] == 'yes').astype(int)
df['internet'] = (df['internet'] == 'yes').astype(int)

X = df[features]
y = df['G3']

print(f"Features: {features}")
print(f"Target: G3 (0-20)")

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"\n📊 Performance:")
print(f"   R² Score: {r2:.3f}")
print(f"   MAE: {mae:.2f} points")
print(f"   RMSE: {np.sqrt(np.mean((y_test - y_pred)**2)):.2f} points")

# Feature importance
feature_importance = pd.DataFrame({
    'Feature': features,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\n📈 Top 5 Features by Importance:")
print(feature_importance.head(5))

# Create SHAP explainer
explainer = shap.TreeExplainer(model)

# Save artifacts
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/student_productivity_model.pkl')
joblib.dump(features, 'models/model_columns.pkl')
joblib.dump(explainer, 'models/shap_explainer.pkl')

print("\n✅ Model artifacts saved to 'models/' folder!")
print("   - student_productivity_model.pkl")
print("   - model_columns.pkl")
print("   - shap_explainer.pkl")

# Quick test
perfect = {f: 0 for f in features}
perfect.update({
    'studytime': 4, 'failures': 0, 'absences': 0,
    'health': 5, 'goout': 1, 'freetime': 1,
    'Dalc': 1, 'Walc': 1, 'famrel': 5,
    'Medu': 4, 'Fedu': 4,
    'schoolsup': 0, 'famsup': 1, 'higher': 1, 'internet': 1,
    'G1': 18, 'G2': 19  # ← PERFECT G1/G2
})

bad = {f: 0 for f in features}
bad.update({
    'studytime': 1, 'failures': 3, 'absences': 30,
    'health': 2, 'goout': 5, 'freetime': 5,
    'Dalc': 5, 'Walc': 5, 'famrel': 1,
    'Medu': 1, 'Fedu': 1,
    'schoolsup': 0, 'famsup': 0, 'higher': 0, 'internet': 0,
    'G1': 6, 'G2': 6  # ← BAD G1/G2
})

perfect_df = pd.DataFrame([perfect])[features]
bad_df = pd.DataFrame([bad])[features]

perfect_pred = model.predict(perfect_df)[0]
bad_pred = model.predict(bad_df)[0]

print("\n🧪 Test Predictions:")
print(f"   Perfect student: {perfect_pred:.1f} / 20")
print(f"   Bad student: {bad_pred:.1f} / 20")
print(f"   Difference: {perfect_pred - bad_pred:.1f} points")