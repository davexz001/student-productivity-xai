"""
MODEL EVALUATION SCRIPT
Run this file anytime to evaluate your model.
Command: python3 evaluate_model.py
"""

import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt

# ==========================================
# LOAD MODEL AND DATA
# ==========================================
print("="*60)
print("📊 LOADING MODEL AND DATA...")
print("="*60)

model = joblib.load('models/student_productivity_model.pkl')
columns = joblib.load('models/model_columns.pkl')
df = pd.read_csv('data/student-mat.csv', sep=';')

# Convert categorical columns
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].map({'yes': 1, 'no': 0}).fillna(df[col])

X = df[columns].apply(pd.to_numeric, errors='coerce').fillna(0)
y = df['G3']
pred = model.predict(X)

print("✅ Model and data loaded successfully!")
print(f"📊 Dataset: {len(df)} records, {len(columns)} features")

# ==========================================
# 1. EVALUATION METRICS
# ==========================================
print("\n" + "="*60)
print("📊 1. EVALUATION METRICS")
print("="*60)

r2 = r2_score(y, pred)
mae = mean_absolute_error(y, pred)
rmse = np.sqrt(mean_squared_error(y, pred))

print(f"R² Score:        {r2:.4f}")
print(f"MAE:             {mae:.2f} points")
print(f"RMSE:            {rmse:.2f} points")
print("="*60)

# ==========================================
# 2. CROSS-VALIDATION
# ==========================================
print("\n" + "="*60)
print("🔄 2. CROSS-VALIDATION (5-Fold)")
print("="*60)

cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
print(f"CV Scores:   {cv_scores}")
print(f"Mean CV R²:  {cv_scores.mean():.4f}")
print(f"Std Dev:     {cv_scores.std():.4f}")
print("="*60)

# ==========================================
# 3. FEATURE IMPORTANCE
# ==========================================
print("\n" + "="*60)
print("📈 3. FEATURE IMPORTANCE (Top 10)")
print("="*60)

importance = pd.DataFrame({'Feature': columns, 'Importance': model.feature_importances_})
importance = importance.sort_values('Importance', ascending=False)
for i, row in importance.head(10).iterrows():
    print(f"{row['Feature']:20} → {row['Importance']*100:.1f}%")
print("="*60)

# ==========================================
# 4. SAMPLE PREDICTIONS
# ==========================================
print("\n" + "="*60)
print("📈 4. SAMPLE PREDICTIONS (First 10 Students)")
print("="*60)
print(f"{'Actual':>8} {'Predicted':>10} {'Error':>10}")
print("-"*30)
for i in range(10):
    actual = y.iloc[i]
    predicted = pred[i]
    error = actual - predicted
    print(f"{actual:>8.0f} {predicted:>10.2f} {error:>+10.2f}")
print("="*60)

# ==========================================
# 5. ERROR DISTRIBUTION
# ==========================================
print("\n" + "="*60)
print("📉 5. ERROR DISTRIBUTION")
print("="*60)

errors = y - pred
print(f"Mean Error:     {errors.mean():.2f}")
print(f"Std Error:      {errors.std():.2f}")
print(f"Min Error:      {errors.min():.2f}")
print(f"Max Error:      {errors.max():.2f}")
within_1 = (abs(errors) < 1).sum()
within_2 = (abs(errors) < 2).sum()
print(f"Errors < 1:     {within_1} / {len(errors)} ({within_1/len(errors)*100:.1f}%)")
print(f"Errors < 2:     {within_2} / {len(errors)} ({within_2/len(errors)*100:.1f}%)")
print("="*60)

# ==========================================
# 6. RISK BAND CLASSIFICATION
# ==========================================
print("\n" + "="*60)
print("🏷️ 6. RISK BAND CLASSIFICATION")
print("="*60)

def get_risk(score):
    if score >= 14:
        return 'High'
    elif score >= 10:
        return 'Moderate'
    else:
        return 'At-Risk'

actual_risk = [get_risk(s) for s in y]
pred_risk = [get_risk(s) for s in pred]

from collections import Counter
print("Actual Distribution:")
for band, count in Counter(actual_risk).items():
    print(f"  {band}: {count} ({count/len(actual_risk)*100:.1f}%)")

print("\nPredicted Distribution:")
for band, count in Counter(pred_risk).items():
    print(f"  {band}: {count} ({count/len(pred_risk)*100:.1f}%)")

correct_risk = sum(1 for a, p in zip(actual_risk, pred_risk) if a == p)
print(f"\n✅ Risk Band Accuracy: {correct_risk}/{len(y)} ({correct_risk/len(y)*100:.1f}%)")
print("="*60)

# ==========================================
# 7. GRADE LETTER ACCURACY (A-F)
# ==========================================
print("\n" + "="*60)
print("📝 7. GRADE LETTER ACCURACY (A-F)")
print("="*60)

def get_grade(score):
    if score >= 16: return 'A'
    elif score >= 14: return 'B'
    elif score >= 12: return 'C'
    elif score >= 10: return 'D'
    else: return 'F'

actual_grade = [get_grade(s) for s in y]
pred_grade = [get_grade(s) for s in pred]

correct_grade = sum(1 for a, p in zip(actual_grade, pred_grade) if a == p)
print(f"Grade Accuracy: {correct_grade}/{len(y)} ({correct_grade/len(y)*100:.1f}%)")
print("="*60)

# ==========================================
# 8. SHAP EXPLANATION (Sample)
# ==========================================
print("\n" + "="*60)
print("🧠 8. SHAP EXPLANATION (First Student)")
print("="*60)

try:
    import shap
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X.iloc[:1])
    
    print("Feature contributions for Student 1:")
    base_value = explainer.expected_value
    print(f"Base Value: {base_value:.2f}")
    
    # Get top 5 contributors for first student
    sv = shap_values.values[0]
    for i in np.argsort(np.abs(sv))[-5:][::-1]:
        feature = columns[i]
        value = sv[i]
        print(f"  {feature}: {value:+.2f} (feature value = {X.iloc[0, i]:.2f})")
    print(f"\nFinal Prediction: {base_value + sv.sum():.2f} / 20")
except Exception as e:
    print(f"SHAP explanation skipped: {e}")

print("\n" + "="*60)
print("✅ EVALUATION COMPLETE!")
print("="*60)