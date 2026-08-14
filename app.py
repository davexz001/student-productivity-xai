import os
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import shap
from auth import verify_credentials, register_student, get_all_users

st.set_page_config(page_title="Student Productivity XAI Portal", layout="wide")

# Initialize Session State Variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None


def login_screen():
    st.title("Student Productivity XAI Portal - Access Gateway")
    
    tab1, tab2 = st.tabs(["Login", "Student Registration"])
    
    with tab1:
        st.subheader("Account Authentication")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            valid, role = verify_credentials(username, password)
            if valid:
                st.session_state.authenticated = True
                st.session_state.role = role
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    with tab2:
        st.subheader("New Student Self-Registration")
        st.caption("Notice: Student accounts can be self-registered below. Counselor and Admin credentials are pre-provisioned by system administrators.")
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Register Student Account"):
            if not new_user or not new_pass:
                st.error("Please provide both a username and password.")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match.")
            else:
                success, msg = register_student(new_user, new_pass)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)


def load_artifacts():
    model_path = "models/student_productivity_model.pkl"
    columns_path = "models/model_columns.pkl"
    explainer_path = "models/shap_explainer.pkl"

    if not (os.path.exists(model_path) and os.path.exists(columns_path) and os.path.exists(explainer_path)):
        st.error("Model artifacts missing! Please execute 'python3 train.py' in your terminal environment.")
        st.stop()

    model = joblib.load(model_path)
    columns = joblib.load(columns_path)
    explainer = joblib.load(explainer_path)
    return model, columns, explainer


# ==========================================
# 1. STUDENT SELF-SERVICE PORTAL
# ==========================================
def render_student_dashboard(model, columns, explainer):
    st.header(f"Student Portal - Self-Diagnostic Tool ({st.session_state.username})")
    st.write("Input your academic habits and lifestyle parameters to evaluate your predicted productivity trajectory and diagnostic factor attributions.")

    st.subheader("Academic Routine & Behavioral Input")

    col1, col2, col3 = st.columns(3)
    with col1:
        studytime = st.slider("Weekly Study Time (1: <2h, 2: 2-5h, 3: 5-10h, 4: >10h)", 1, 4, 2)
        failures = st.slider("Past Class Failures", 0, 4, 0)
        higher = st.selectbox("Planning for Higher Education?", ["yes", "no"])

    with col2:
        absences = st.slider("School Absences", 0, 93, 4)
        health = st.slider("Current Health Status (1: Poor, 5: Excellent)", 1, 5, 4)
        schoolsup = st.selectbox("Extra Educational Support?", ["no", "yes"])

    with col3:
        goout = st.slider("Going Out with Friends (1: Low, 5: High)", 1, 5, 3)
        internet = st.selectbox("Internet Access at Home?", ["yes", "no"])
        famsup = st.selectbox("Family Educational Support?", ["yes", "no"])

    if st.button("Evaluate Trajectory", type="primary"):
        payload = {
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

        input_df = pd.DataFrame([payload])[columns]
        prediction = model.predict(input_df)[0]
        prediction_clipped = np.clip(prediction, 1.0, 20.0)

        st.markdown("---")
        st.subheader("Performance Projection")
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric(label="Estimated Final Productivity Score", value=f"{prediction_clipped:.2f} / 20")
        with m2:
            if prediction_clipped >= 13:
                st.success("Status: High Academic Productivity Potential")
            elif prediction_clipped >= 10:
                st.warning("Status: Moderate Academic Productivity - Improvement Recommended")
            else:
                st.error("Status: High Academic Risk Group (Intervention Advised)")

        st.markdown("---")
        st.subheader("Personalized SHAP Diagnostic Attribution")
        shap_values = explainer(input_df)
        fig, ax = plt.subplots(figsize=(10, 4.5))
        shap.plots.waterfall(shap_values[0], show=False)
        st.pyplot(fig)
        plt.close("all")

        st.markdown("---")
        st.subheader("Automated Habit Guidance")
        if studytime < 3:
            st.info("Study Habit Tip: Increasing weekly self-study time above 5 hours correlates strongly with higher academic performance.")
        if goout >= 4:
            st.info("Balance Tip: High frequency of social outings detected. Balancing social activities with structured study blocks stabilizes exam performance.")
        if absences > 5:
            st.warning("Attendance Warning: Frequent absences significantly lower projected trajectories. Consider consulting an academic advisor.")


# ==========================================
# 2. COUNSELOR DIAGNOSTIC & SIMULATION PORTAL
# ==========================================
def render_counselor_dashboard(model, columns, explainer):
    st.header("Counselor Portal - Risk Triage & Behavioral Simulator")
    st.write("Perform individual student risk diagnoses, run what-if scenario simulations, and extract SHAP explainability insights.")

    tab1, tab2 = st.tabs(["Individual Student Diagnostic", "What-If Scenario Simulator"])

    # --- TAB 1: INDIVIDUAL DIAGNOSTIC ---
    with tab1:
        st.subheader("Student Behavioral Profile Evaluation")

        col1, col2, col3 = st.columns(3)
        with col1:
            studytime = st.slider("Weekly Study Time (1-4)", 1, 4, 2, key="c_study")
            failures = st.slider("Past Class Failures", 0, 4, 1, key="c_fail")
            higher = st.selectbox("Higher Education Ambition?", ["yes", "no"], key="c_high")

        with col2:
            absences = st.slider("School Absences", 0, 93, 8, key="c_abs")
            health = st.slider("Health Status (1-5)", 1, 5, 3, key="c_health")
            schoolsup = st.selectbox("Extra Educational Support?", ["no", "yes"], key="c_supp")

        with col3:
            goout = st.slider("Going Out Frequency (1-5)", 1, 5, 4, key="c_goout")
            famsup = st.selectbox("Family Educational Support?", ["yes", "no"], key="c_famsup")
            internet = st.selectbox("Home Internet Access?", ["yes", "no"], key="c_net")

        if st.button("Run Diagnostic Assessment", type="primary"):
            payload = {
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

            input_df = pd.DataFrame([payload])[columns]
            prediction = model.predict(input_df)[0]
            prediction_clipped = np.clip(prediction, 1.0, 20.0)

            st.markdown("---")
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

            st.markdown("---")
            st.subheader("SHAP Root Cause Attribution Waterfall Plot")
            
            shap_values = explainer(input_df)
            fig, ax = plt.subplots(figsize=(10, 4.5))
            shap.plots.waterfall(shap_values[0], show=False)
            st.pyplot(fig)
            plt.close("all")

            st.markdown("---")
            st.subheader("Counselor Intervention Record Log")
            notes = f"""=== ACADEMIC ADVISING SESSION SUMMARY ===
• Student Profile: Failures={failures} | Absences={absences} | Study Time Level={studytime}
• Predicted Outcome: {prediction_clipped:.2f} / 20
• Core Negative Risk Drivers: {'High Absences' if absences > 5 else ''} {'Low Study Time' if studytime < 3 else ''} {'High Outings' if goout >= 4 else ''}
• Action Plan: Recommended increase in study hours to level {min(4, studytime+1)} and regular attendance monitoring.
"""
            st.code(notes, language="text")

    # --- TAB 2: WHAT-IF SCENARIO SIMULATOR ---
    with tab2:
        st.subheader("Lifestyle Change Scenario Simulator")
        st.write("Compare current student metrics against an improved target habits scenario to demonstrate potential score gains.")

        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("#### Current Baseline Profile")
            curr_study = st.slider("Current Weekly Study Time", 1, 4, 1, key="sim_cstudy")
            curr_abs = st.slider("Current Absences", 0, 50, 12, key="sim_cabs")
            curr_goout = st.slider("Current Outing Level", 1, 5, 4, key="sim_cgo")
            curr_fail = st.slider("Current Past Failures", 0, 4, 1, key="sim_cfail")

        with sc2:
            st.markdown("#### Target Lifestyle Goals")
            targ_study = st.slider("Target Weekly Study Time", 1, 4, 3, key="sim_tstudy")
            targ_abs = st.slider("Target Absences Goal", 0, 50, 3, key="sim_tabs")
            targ_goout = st.slider("Target Outing Level", 1, 5, 2, key="sim_tgo")
            targ_fail = curr_fail  # Fixed baseline

        if st.button("Simulate Impact", type="primary"):
            curr_payload = {
                "studytime": curr_study, "failures": curr_fail, "absences": curr_abs, 
                "health": 3, "goout": curr_goout, "freetime": 3, "Dalc": 1, "Walc": 1, 
                "famrel": 4, "Medu": 3, "Fedu": 3, "schoolsup": 0, "famsup": 1, 
                "higher": 1, "internet": 1
            }
            targ_payload = {
                "studytime": targ_study, "failures": targ_fail, "absences": targ_abs, 
                "health": 3, "goout": targ_goout, "freetime": 3, "Dalc": 1, "Walc": 1, 
                "famrel": 4, "Medu": 3, "Fedu": 3, "schoolsup": 0, "famsup": 1, 
                "higher": 1, "internet": 1
            }

            p_curr = np.clip(model.predict(pd.DataFrame([curr_payload])[columns])[0], 1.0, 20.0)
            p_targ = np.clip(model.predict(pd.DataFrame([targ_payload])[columns])[0], 1.0, 20.0)
            diff = p_targ - p_curr

            st.markdown("---")
            res1, res2, res3 = st.columns(3)
            with res1:
                st.metric("Current Projected Score", f"{p_curr:.2f} / 20")
            with res2:
                st.metric("Target Projected Score", f"{p_targ:.2f} / 20")
            with res3:
                st.metric("Potential Trajectory Delta", f"+{diff:.2f} pts", delta_color="normal")


# ==========================================
# 3. ADMINISTRATIVE EXECUTIVE PORTAL
# ==========================================
def render_admin_dashboard(model, columns):
    st.header("Admin Portal - Executive System Oversight")
    st.write("Manage user role governance, inspect registered database accounts, and execute batch cohort predictions.")
    
    tab1, tab2 = st.tabs(["User Management Audit", "Batch Cohort Assessment"])

    with tab1:
        st.subheader("Registered User Account Database")
        users = get_all_users()
        user_df = pd.DataFrame(users, columns=["User ID", "Username", "Assigned Role"])
        st.dataframe(user_df, use_container_width=True)

    with tab2:
        st.subheader("Cohort Batch Processing Engine")
        st.write("Upload a CSV file containing multiple student behavioral records to execute batch productivity predictions.")
        uploaded_file = st.file_uploader("Upload Student Cohort Dataset (CSV)", type=["csv"])
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.getvalue().decode("utf-8")
                delimiter = ";" if ";" in content else ","
                uploaded_file.seek(0)
                batch_data = pd.read_csv(uploaded_file, sep=delimiter)
                st.write(f"Dataset successfully loaded. Total Records: {len(batch_data)}")
                
                if st.button("Execute Batch Prediction Engine", type="primary"):
                    # Fill missing model schema columns with safe dataset medians
                    for col in columns:
                        if col not in batch_data.columns:
                            batch_data[col] = 0
                            
                    batch_inputs = batch_data[columns]
                    preds = model.predict(batch_inputs)
                    batch_data["Predicted_G3_Score"] = np.clip(preds, 1.0, 20.0)
                    
                    st.markdown("---")
                    st.subheader("Batch Assessment Results")
                    st.dataframe(batch_data[["Predicted_G3_Score"] + [c for c in columns if c in batch_data.columns]], use_container_width=True)
            except Exception as e:
                st.error(f"Error processing uploaded batch CSV file: {str(e)}")


def main_dashboard():
    st.sidebar.title("Navigation Panel")
    st.sidebar.text(f"Authenticated User: {st.session_state.username}")
    st.sidebar.text(f"Active Role: {st.session_state.role}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

    model, columns, explainer = load_artifacts()

    # Enforce Role-Based Access Control (RBAC) routing
    if st.session_state.role == "Student":
        render_student_dashboard(model, columns, explainer)
    elif st.session_state.role == "Counselor":
        render_counselor_dashboard(model, columns, explainer)
    elif st.session_state.role == "Admin":
        render_admin_dashboard(model, columns)
    else:
        st.error("Unauthorized user role detected in session state.")


if not st.session_state.authenticated:
    login_screen()
else:
    main_dashboard()