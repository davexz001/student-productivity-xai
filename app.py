import os
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import shap

# Import functions from custom local modules
from database import init_db, authenticate_user, register_user, save_assessment
from pdf_generator import generate_student_pdf

# Initialize Database on launch
init_db()

# Page Configuration
st.set_page_config(
    page_title="EduSphere AI Portal", 
    layout="wide",
    initial_sidebar_state="auto"
)

# Custom Enterprise CSS Engine
st.markdown("""
    <style>
    /* Global Canvas Styling */
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Default Streamlit Footer and Main Menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Force Visibility for Widget Labels */
    label, div[data-widget="stSlider"] label, div[data-baseweb="select"] label, p {
        color: #0F172A !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }
    
    /* Ensure Slider Min/Max Text and Current Values are Visible */
    div[data-testid="stSliderTickBarMin"], div[data-testid="stSliderTickBarMax"], div[data-testid="stWidgetLabel"] p {
        color: #1E293B !important;
    }
    
    /* Top Header Bar */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #FFFFFF;
        padding: 16px 24px;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .welcome-text {
        font-size: 22px;
        font-weight: 700;
        color: #0F172A !important;
        margin: 0;
    }
    .sub-text {
        font-size: 13px;
        color: #475569 !important;
        margin: 0;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    /* Input Card Containers */
    div[data-testid="stForm"], .css-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }

    /* Primary Buttons */
    div.stButton > button:first-child {
        background-color: #2563EB;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3);
    }
    /* Fix text color for Download Buttons */
    div.stDownloadButton > button {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None


# ==========================================
# AUTHENTICATION & LOGIN / REGISTRATION SCREEN
# ==========================================
def login_screen():
    st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="color: #0F172A; font-weight: 800;">EduSphere AI</h1>
            <p style="color: #475569;">Institutional Academic Productivity & Diagnostic Portal</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab_login, tab_register = st.tabs(["Login", "Register Account"])
        
        with tab_login:
            with st.container(border=True):
                username = st.text_input("Username", key="login_user", placeholder="e.g. student1, counselor1")
                password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")

                if st.button("Authenticate", type="primary", use_container_width=True):
                    valid, role = authenticate_user(username, password)
                    if valid:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = role
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password.")

        with tab_register:
            with st.container(border=True):
                new_user = st.text_input("Choose Username", key="reg_user")
                new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
                new_role = st.selectbox("Select Account Role", ["Student", "Counselor", "Admin"], key="reg_role")
                
                if st.button("Create Account", use_container_width=True):
                    if new_user and new_pass:
                        success, msg = register_user(new_user, new_pass, new_role)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please fill in all fields.")


# ==========================================
# UTILITY & ARTIFACT HELPERS
# ==========================================
def load_artifacts():
    model_path = "models/student_productivity_model.pkl"
    columns_path = "models/model_columns.pkl"
    explainer_path = "models/shap_explainer.pkl"

    if not (os.path.exists(model_path) and os.path.exists(columns_path) and os.path.exists(explainer_path)):
        st.error("Model artifacts missing! Please run 'python3 train.py' in your terminal first.")
        st.stop()

    model = joblib.load(model_path)
    columns = joblib.load(columns_path)
    explainer = joblib.load(explainer_path)
    return model, columns, explainer


def build_full_payload(g1, g2, studytime, failures, absences, health, goout, higher, internet, schoolsup, famsup, columns):
    """Utility helper to build complete feature-aligned row matching schema."""
    payload = {
        "G1": g1,
        "G2": g2,
        "studytime": studytime,
        "failures": failures,
        "absences": absences,
        "health": health,
        "goout": goout,
        "freetime": 3,
        "Dalc": 1,
        "Walc": 1,
        "famrel": 4,
        "Medu": 3,
        "Fedu": 3,
        "schoolsup": 1 if schoolsup == "yes" else 0,
        "famsup": 1 if famsup == "yes" else 0,
        "higher": 1 if higher == "yes" else 0,
        "internet": 1 if internet == "yes" else 0,
    }
    
    df = pd.DataFrame([payload])
    return df.reindex(columns=columns, fill_value=0)


# ==========================================
# 1. STUDENT DASHBOARD
# ==========================================
def render_student_dashboard(model, columns):
    st.markdown("""
        <div class="top-bar">
            <div>
                <p class="welcome-text">Student Self-Service Portal</p>
                <p class="sub-text">Log your academic history and weekly study habits to project your performance trajectory.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("Academic History & Weekly Habits")

        col1, col2 = st.columns(2)
        with col1:
            g1 = st.slider("First Period Grade - G1 (0–20 Scale)", 0, 20, 12, key="st_g1")
            g2 = st.slider("Second Period Grade - G2 (0–20 Scale)", 0, 20, 12, key="st_g2")
            
            studytime_labels = {
                "1: Less than 2 hours": 1,
                "2: 2 to 5 hours": 2,
                "3: 5 to 10 hours": 3,
                "4: More than 10 hours": 4
            }
            selected_study = st.selectbox("Weekly Study Time", list(studytime_labels.keys()), index=2, key="st_study")
            studytime = studytime_labels[selected_study]

        with col2:
            health_labels = {
                "1: Very Poor": 1,
                "2: Poor": 2,
                "3: Fair": 3,
                "4: Good": 4,
                "5: Excellent": 5
            }
            selected_health = st.selectbox("Current Health Status", list(health_labels.keys()), index=3, key="st_health")
            health = health_labels[selected_health]

            goout_labels = {
                "1: Very Low": 1,
                "2: Low": 2,
                "3: Moderate": 3,
                "4: High": 4,
                "5: Very High": 5
            }
            selected_goout = st.selectbox("Going Out with Friends", list(goout_labels.keys()), index=1, key="st_go")
            goout = goout_labels[selected_goout]

            absences = st.slider("School Absences (Days)", 0, 93, 2, key="st_abs")
            internet = st.selectbox("Internet Access at Home?", ["yes", "no"], key="st_net")
            higher = st.selectbox("Planning for Higher Education?", ["yes", "no"], key="st_high")

        eval_btn = st.button("Evaluate Trajectory", type="primary", use_container_width=True)

    if eval_btn:
        input_df = build_full_payload(g1, g2, studytime, 0, absences, health, goout, higher, internet, "no", "yes", columns)
        prediction = model.predict(input_df)[0]
        prediction_clipped = float(np.clip(prediction, 1.0, 20.0))

        risk_status = "High Risk"
        if prediction_clipped >= 13:
            risk_status = "Low Risk (Distinction Target)"
        elif prediction_clipped >= 10:
            risk_status = "Moderate Risk"

        # Log entry to database
        save_assessment(st.session_state.username, g1, g2, prediction_clipped, risk_status)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Performance Projection")
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric(label="Estimated Final Score (0-20 Scale)", value=f"{prediction_clipped:.2f} / 20")
        with m2:
            if prediction_clipped >= 13:
                st.success("Status: On Track for Academic Distinction")
            elif prediction_clipped >= 10:
                st.warning("Status: Moderate Progress - Improvement Possible")
            else:
                st.error("Status: High Academic Risk Group")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.subheader("Actionable Recommendations & Export Options")
            if studytime < 3:
                st.info("Study Habit Tip: Increasing your weekly self-study time above 5 hours significantly correlates with higher final grades.")
            if goout >= 4:
                st.info("Balance Tip: High social outing frequency detected. Balancing leisure activities with structured study blocks can stabilize exam scores.")
            if absences > 5:
                st.warning("Attendance Warning: Frequent absences strongly depress score trajectories. Consider scheduling time with your academic advisor.")

            # PDF Download Generation
            pdf_bytes = generate_student_pdf(
                username=st.session_state.username,
                g1=g1, g2=g2,
                predicted=prediction_clipped,
                risk=risk_status,
                studytime=studytime,
                absences=absences
            )
            
            st.download_button(
                label="📄 Download Diagnostic PDF Report",
                data=pdf_bytes,
                file_name=f"{st.session_state.username}_academic_report.pdf",
                mime="application/pdf"
            )


# ==========================================
# 2. COUNSELOR & ADMIN DIAGNOSTIC DASHBOARD
# ==========================================
def render_counselor_dashboard(model, columns, explainer):
    st.markdown("""
        <div class="top-bar">
            <div>
                <p class="welcome-text">Counselor & Admin Diagnostic Workspace</p>
                <p class="sub-text">Perform individual risk triage, inspect SHAP root-cause feature vectors, and model what-if scenarios.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Individual Student Diagnostic", "What-If Scenario Simulator"])

    # --- TAB 1: INDIVIDUAL DIAGNOSTIC ---
    with tab1:
        with st.container(border=True):
            st.subheader("Student Evaluation Profile")

            col1, col2, col3 = st.columns(3)
            with col1:
                g1 = st.slider("First Period Grade (G1)", 0, 20, 10, key="c_g1")
                g2 = st.slider("Second Period Grade (G2)", 0, 20, 10, key="c_g2")
                
                studytime_labels = {"1: Less than 2 hours": 1, "2: 2 to 5 hours": 2, "3: 5 to 10 hours": 3, "4: More than 10 hours": 4}
                study_choice = st.selectbox("Weekly Study Time", list(studytime_labels.keys()), index=1, key="c_study")
                studytime = studytime_labels[study_choice]

            with col2:
                fail_labels = {"0: None": 0, "1: 1 Failure": 1, "2: 2 Failures": 2, "3: 3 Failures": 3, "4: 4+ Failures": 4}
                fail_choice = st.selectbox("Past Class Failures", list(fail_labels.keys()), index=1, key="c_fail")
                failures = fail_labels[fail_choice]

                absences = st.slider("School Absences (Days)", 0, 93, 8, key="c_abs")
                
                health_labels = {"1: Very Poor": 1, "2: Poor": 2, "3: Fair": 3, "4: Good": 4, "5: Excellent": 5}
                health_choice = st.selectbox("Health Status", list(health_labels.keys()), index=2, key="c_health")
                health = health_labels[health_choice]

            with col3:
                goout_labels = {"1: Very Low": 1, "2: Low": 2, "3: Moderate": 3, "4: High": 4, "5: Very High": 5}
                goout_choice = st.selectbox("Going Out Frequency", list(goout_labels.keys()), index=3, key="c_goout")
                goout = goout_labels[goout_choice]

                higher = st.selectbox("Wants Higher Education?", ["yes", "no"], key="c_high")
                schoolsup = st.selectbox("Extra Educational Support?", ["no", "yes"], key="c_supp")
                famsup = st.selectbox("Family Educational Support?", ["yes", "no"], key="c_famsup")
                internet = st.selectbox("Home Internet Access?", ["yes", "no"], key="c_net")

            diag_btn = st.button("Run Diagnostic Assessment", type="primary", key="btn_diag", use_container_width=True)

        if diag_btn:
            input_df = build_full_payload(g1, g2, studytime, failures, absences, health, goout, higher, internet, schoolsup, famsup, columns)
            prediction = model.predict(input_df)[0]
            prediction_clipped = float(np.clip(prediction, 1.0, 20.0))

            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            with m1:
                st.metric(label="Predicted Final Score", value=f"{prediction_clipped:.2f} / 20")
            with m2:
                if prediction_clipped >= 13:
                    st.success("Triage Status: Low Risk")
                elif prediction_clipped >= 10:
                    st.warning("Triage Status: Moderate Risk")
                else:
                    st.error("Triage Status: High Risk (Intervention Required)")

            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.subheader("SHAP Root Cause Attribution Waterfall")
                
                shap_values = explainer(input_df)
                fig, ax = plt.subplots(figsize=(10, 4.5))
                fig.patch.set_facecolor('#FFFFFF')
                shap.plots.waterfall(shap_values[0], show=False)
                st.pyplot(fig)
                plt.close("all")

    # --- TAB 2: WHAT-IF SCENARIO SIMULATOR ---
    with tab2:
        st.subheader("Lifestyle Change Scenario Simulator")
        st.caption("Compare current baseline metrics against improved target habits to demonstrate projected score gains.")

        sc1, sc2 = st.columns(2)
        with sc1:
            with st.container(border=True):
                st.markdown("#### Current Baseline Profile")
                curr_g1 = st.slider("Current G1 Score", 0, 20, 8, key="sim_cg1")
                curr_g2 = st.slider("Current G2 Score", 0, 20, 8, key="sim_cg2")
                
                curr_study_choice = st.selectbox("Current Weekly Study Time", ["1: Less than 2h", "2: 2 to 5h", "3: 5 to 10h", "4: More than 10h"], index=0, key="sim_cstudy")
                curr_study = int(curr_study_choice.split(":")[0])

                curr_goout_choice = st.selectbox("Current Social Outings", ["1: Very Low", "2: Low", "3: Moderate", "4: High", "5: Very High"], index=3, key="sim_cgo")
                curr_goout = int(curr_goout_choice.split(":")[0])

                curr_abs = st.slider("Current Absences", 0, 50, 15, key="sim_cabs")

        with sc2:
            with st.container(border=True):
                st.markdown("#### Target Intervention Goals")
                targ_g1 = curr_g1
                targ_g2 = curr_g2

                targ_study_choice = st.selectbox("Target Weekly Study Time Goal", ["1: Less than 2h", "2: 2 to 5h", "3: 5 to 10h", "4: More than 10h"], index=2, key="sim_tstudy")
                targ_study = int(targ_study_choice.split(":")[0])

                targ_goout_choice = st.selectbox("Target Social Outings Goal", ["1: Very Low", "2: Low", "3: Moderate", "4: High", "5: Very High"], index=1, key="sim_tgo")
                targ_goout = int(targ_goout_choice.split(":")[0])

                targ_abs = st.slider("Target Absences Goal", 0, 50, 2, key="sim_tabs")

        sim_btn = st.button("Simulate Intervention Impact", type="primary", key="btn_sim", use_container_width=True)

        if sim_btn:
            curr_df = build_full_payload(curr_g1, curr_g2, curr_study, 1, curr_abs, 3, curr_goout, "yes", "yes", "no", "yes", columns)
            targ_df = build_full_payload(targ_g1, targ_g2, targ_study, 1, targ_abs, 3, targ_goout, "yes", "yes", "no", "yes", columns)

            p_curr = float(np.clip(model.predict(curr_df)[0], 1.0, 20.0))
            p_targ = float(np.clip(model.predict(targ_df)[0], 1.0, 20.0))
            diff = p_targ - p_curr

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Simulation Results Comparison")

            res1, res2, res3 = st.columns(3)
            with res1:
                st.metric("Current Baseline Score", f"{p_curr:.2f} / 20")
            with res2:
                st.metric("Target Projected Score", f"{p_targ:.2f} / 20")
            with res3:
                st.metric("Expected Performance Gain", f"{diff:+.2f} pts", delta=f"{diff:+.2f} pts")

            if diff > 0:
                st.success(f"Positive Trajectory: Adopting target habits generates a +{diff:.2f} point increase in predicted final grade.")
            elif diff < 0:
                st.error(f"Negative Impact: Target settings represent a regression of {diff:.2f} points.")
            else:
                st.info("No Net Change: Adjust target parameters higher to simulate improvements.")


# ==========================================
# MAIN ROUTER
# ==========================================
def main():
    st.sidebar.markdown("### EduSphere Portal")
    st.sidebar.write(f"User: **{st.session_state.username}**")
    st.sidebar.info(f"Role: **{st.session_state.role}**")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

    model, columns, explainer = load_artifacts()

    if st.session_state.role == "Student":
        render_student_dashboard(model, columns)
    elif st.session_state.role in ["Counselor", "Admin"]:
        render_counselor_dashboard(model, columns, explainer)


if not st.session_state.authenticated:
    login_screen()
else:
    main()