# Development of an Explainable Machine Learning Model for Predicting Student Productivity

## 🚀 Live Demo & Interactive Portal

The application is deployed and available live at:
🔗 **[EduSphere AI Web App](https://studentpructivityxai.streamlit.app/)**

### 🔑 Demo Login Credentials
For testing and reviewing role-based capabilities, you can log in using the following credentials or register a new account directly on the login page:

| Role | Username | Password | Access & Features |
| :--- | :--- | :--- | :--- |
| **Student** | `student1` | `password123` | Self-service diagnostic portal, performance projections, actionable advice, PDF report exports. |
| **Counselor** | `counselor1` | `counselor123` | Individual risk triage, SHAP root-cause feature vectors, what-if scenario simulator. |
| **Admin** | `admin1` | `admin123` | System-wide access and administrative controls. |

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

   