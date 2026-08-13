# Development of an Explainable Machine Learning Model for Predicting Student Productivity

## System Architecture & Pipeline
1. **Data Ingestion:** UCI Student Performance Dataset (`student-mat.csv`).
2. **Preprocessing:** Behavioral feature isolation and data leakage prevention (dropping G1 & G2).
3. **Machine Learning:** Random Forest Regressor.
4. **Explainable AI:** SHAP (SHapley Additive exPlanations) for local feature attribution.
5. **Security & Interface:** Streamlit UI with Role-Based Access Control (`auth.py`).

## Setup & Execution
1. Install dependencies:
   `pip install -r requirements.txt`
2. Run model training pipeline:
   `python3 train.py`
3. Launch web app:
   `streamlit run app.py`