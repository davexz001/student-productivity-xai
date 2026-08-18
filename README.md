# 🏫 EduSphere AI: Explainable Machine Learning Platform for Student Productivity & Performance Prediction

An end-to-end, role-based Explainable AI (XAI) web platform designed to predict final academic trajectories ($G3$) using behavioral indicators, provide root-cause feature attribution via SHAP waterfall plots, simulate intervention strategies, and export downloadable PDF diagnostic reports.

---

## 🚀 Live Demo & Interactive Portal

The application is deployed live and publicly accessible at:
🔗 **[EduSphere AI Web App](https://studentpructivityxai.streamlit.app/)**

### 🔑 Demo Login Credentials
Use the credentials below to test the platform across different roles, or register a new user directly via the **Register Account** tab on the login screen:

| Role | Username | Password | Access & Key Features |
| :--- | :--- | :--- | :--- |
| **Student** | `student1` | `student123` | Self-service diagnostic portal, performance projections, actionable guidance, PDF diagnostic download. |
| **Counselor** | `counselor` | `counselor123` | Risk triage, SHAP root-cause feature vectors, what-if intervention simulator. |
| **Admin** | `admin` | `admin123` | System-wide administrative controls and user management oversight. |

---

## 🛠️ System Architecture & Pipeline

1. **Data Ingestion:** UCI Student Performance Dataset (`student-mat.csv`).
2. **Preprocessing & Feature Engineering:** Behavioral feature isolation, categorical mapping, and model artifact serialization (`models/`).
3. **Machine Learning Core:** Ensemble Random Forest Regressor optimized to project student final performance scores ($G3$).
4. **Explainable AI (XAI):** SHAP (SHapley Additive exPlanations) engine delivering local feature attribution waterfall plots and interactive what-if scenario simulators for counselor intervention planning.
5. **Database & Security Layer:** SQLite engine (`database.py`) providing SHA-256 password hashing, user registration, and assessment history persistence under Role-Based Access Control (**Student**, **Counselor**, **Admin**).
6. **Reporting Engine:** Integrated PDF report generator (`pdf_generator.py` using `fpdf2`) outputting downloadable, standardized student diagnostic summaries.
7. **User Interface & Cloud Hosting:** Streamlit SaaS dashboard (`app.py`) continuously deployed via **Streamlit Community Cloud**.

---

## 📂 Project Directory Structure

```text
student-productivity-xai/
├── app.py                  # Main multi-tab Streamlit web application
├── database.py             # SQLite database engine (auth, users, assessment logs)
├── pdf_generator.py        # FPDF diagnostic PDF generation engine
├── train.py                # ML pipeline training and artifact exporter
├── requirements.txt        # Project dependencies for cloud runtime
├── data/
│   └── student-mat.csv     # UCI Student Performance raw dataset
└── models/
    ├── student_productivity_model.pkl  # Trained Random Forest model
    ├── model_columns.pkl              # Feature column alignments
    └── shap_explainer.pkl             # Serialized SHAP explainer

    Setup & Execution Guide
Option A: Local / GitHub Codespaces
Clone the repository:

Bash
git clone [https://github.com/davexz001/student-productivity-xai.git](https://github.com/davexz001/student-productivity-xai.git)
cd student-productivity-xai
Install dependencies:

Bash
pip install -r requirements.txt
Train the ML model & generate artifacts:

Bash
python3 train.py
Launch the web interface:

Bash
streamlit run app.py
Option B: Cloud Deployment (Streamlit Cloud)
To deploy your own fork to Streamlit Community Cloud:

Push your repository to GitHub (main branch).

Visit share.streamlit.io and connect your GitHub account.

Select your repository, set the branch to main, and specify app.py as the main file path.

Click Deploy!

📜 License
This project is open-source and available under the MIT License.
