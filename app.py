import streamlit as st
import os
import joblib
import pandas as pd
import numpy as np
from auth import verify_credentials, register_student, get_all_users

from dashboards.student_dashboard import render_student_dashboard
from dashboards.counselor_dashboard import render_counselor_dashboard
from dashboards.admin_dashboard import render_admin_dashboard
from styles import SLIDER_CSS

st.set_page_config(
    page_title="EduVantage XAI Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SESSION STATE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None


# ==========================================
# PROFESSIONAL UI CSS
# ==========================================
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: #F8FAFC;
    }
    
    .main > div {
        padding-top: 0;
    }
    
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }
    
    /* ===== TYPOGRAPHY ===== */
    h1 {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #1E293B !important;
        letter-spacing: -0.3px !important;
        margin-bottom: 4px !important;
    }
    h2 {
        font-size: 22px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        margin-top: 12px !important;
        margin-bottom: 4px !important;
    }
    h3 {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        margin-top: 8px !important;
        margin-bottom: 4px !important;
    }
    p, li, label, .stMarkdown, .stText {
        font-size: 14px !important;
        color: #334155 !important;
        line-height: 1.6 !important;
    }
    
    /* ===== CARDS ===== */
    .card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
    }
    .card-header {
        font-size: 16px;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* ===== BUTTONS — Lighter blue ===== */
    .stButton > button {
        background: #818CF8 !important;
        color: #1E1B4B !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        font-size: 14px !important;
        box-shadow: 0 2px 8px rgba(129, 140, 248, 0.3) !important;
    }
    .stButton > button:hover {
        background: #6366F1 !important;
        color: #0F0A2A !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        color: #1E293B !important;
        font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #818CF8 !important;
        box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2) !important;
    }
    
    /* ===== SELECTBOX ===== */
    .stSelectbox > div > div > div > div {
        background: #FFFFFF !important;
        color: #1E293B !important;
    }
    
    /* ===== TABS ===== */
    .stTabs > div > div > button {
        color: #64748B !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-size: 14px !important;
    }
    .stTabs > div > div > button[aria-selected="true"] {
        color: #4F46E5 !important;
        background: #EEF2FF !important;
    }
    
    /* ===== EXPANDERS ===== */
    .stExpander {
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        background: #FFFFFF !important;
    }
    
    /* ===== POPOVER (3-dot menu) ===== */
    .stPopover > button {
        background: transparent !important;
        color: #64748B !important;
        font-size: 28px !important;
        padding: 0 10px !important;
        border: none !important;
        box-shadow: none !important;
    }
    .stPopover > button:hover {
        background: transparent !important;
        color: #1E293B !important;
    }
    
    /* ===== ALERTS ===== */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid !important;
        background: #F8FAFC !important;
        font-size: 14px !important;
    }
    
    /* ===== METRIC ===== */
    .stMetric {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #E2E8F0;
    }
    .stMetric label {
        color: #64748B !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }
    
    /* ===== DATAFRAME ===== */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #E2E8F0 !important;
        font-size: 14px !important;
    }
    .dataframe thead tr th {
        background: #F1F5F9 !important;
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    .dataframe tbody tr td {
        font-size: 14px !important;
        color: #334155 !important;
    }
    
    /* ===== SHAP PLOT — CONTROLLED SIZE ===== */
    .stImage {
        max-width: 100% !important;
    }
    .stPlotlyChart {
        max-width: 100% !important;
    }
    .stImage img {
        max-width: 800px !important;
        width: 100% !important;
        height: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# ===== SLIDER CSS (MOVED OUTSIDE THE STYLE BLOCK) =====
st.markdown(SLIDER_CSS, unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================
def render_header():
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="
                background: #4F46E5;
                width: 44px;
                height: 44px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                font-weight: 700;
                color: white;
                flex-shrink: 0;
            ">🎓</div>
            <div>
                <span style="color: #1E293B; font-size: 20px; font-weight: 700; letter-spacing: -0.3px;">
                    EduVantage
                </span>
                <span style="color: #64748B; font-size: 14px; margin-left: 8px; font-weight: 400;">
                    XAI Portal
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 8px;">
            <span style="color: #64748B; font-size: 14px; font-weight: 500;">
                👤 {st.session_state.role}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        with st.popover("☰", use_container_width=True):
            st.markdown("### Menu")
            st.markdown("---")
            if st.button("Dashboard", use_container_width=True):
                st.rerun()
            if st.button("My Profile", use_container_width=True):
                st.info("Profile feature coming soon")
            if st.button("Help", use_container_width=True):
                st.info("Help documentation coming soon")
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.role = None
                st.session_state.username = None
                st.rerun()


# ==========================================
# FOOTER — Dark with white text
# ==========================================
def render_footer():
    st.markdown("""
    <div style="
        background: #1E293B;
        padding: 18px 40px;
        margin: 20px -50px -20px -50px;
        text-align: center;
        border-top: 1px solid #334155;
    ">
        <span style="color: #E2E8F0; font-size: 14px; font-weight: 400;">
            © 2026 EduVantage XAI Portal
        </span>
        <span style="color: #475569; margin: 0 12px;">|</span>
        <span style="color: #94A3B8; font-size: 14px;">
            Built with Streamlit & Machine Learning
        </span>
        <span style="color: #475569; margin: 0 12px;">|</span>
        <span style="color: #94A3B8; font-size: 14px;">
            v2.0 · Research Only
        </span>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# LOGIN SCREEN
# ==========================================
def login_screen():
    st.markdown("""
    <div style="text-align: center; padding: 60px 0 30px 0;">
        <div style="
            background: #4F46E5;
            width: 80px;
            height: 80px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            margin-bottom: 16px;
            box-shadow: 0 8px 30px rgba(79, 70, 229, 0.3);
        ">🎓</div>
        <h1 style="color: #1E293B; font-size: 32px; margin: 10px 0 4px 0; font-weight: 700;">
            EduVantage XAI
        </h1>
        <p style="color: #64748B; font-size: 16px; font-weight: 400;">
            Explainable AI for Student Productivity
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Account Authentication")
            username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")

            if st.button("Login", type="primary", use_container_width=True):
                valid, role = verify_credentials(username, password)
                if valid:
                    st.session_state.authenticated = True
                    st.session_state.role = role
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

        with tab2:
            st.subheader("Student Registration")
            new_user = st.text_input("Choose Username", key="reg_user", placeholder="Create a username")
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass", placeholder="Create a password")
            confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Confirm password")

            if st.button("Register", type="primary", use_container_width=True):
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
    st.stop()


# ==========================================
# LOAD ARTIFACTS
# ==========================================
def load_artifacts():
    model_path = "models/student_productivity_model.pkl"
    columns_path = "models/model_columns.pkl"
    explainer_path = "models/shap_explainer.pkl"

    if not (os.path.exists(model_path) and os.path.exists(columns_path) and os.path.exists(explainer_path)):
        st.error("❌ Model artifacts missing! Please execute 'python3 train.py' in your terminal environment.")
        st.stop()

    model = joblib.load(model_path)
    columns = joblib.load(columns_path)
    explainer = joblib.load(explainer_path)
    return model, columns, explainer


# ==========================================
# MAIN DASHBOARD
# ==========================================
def main_dashboard():
    render_header()

    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        st.markdown(f"**User:** `{st.session_state.username}`")
        st.markdown(f"**Role:** `{st.session_state.role}`")
        st.markdown("---")

    model, columns, explainer = load_artifacts()

    if st.session_state.role == "Student":
        render_student_dashboard(model, columns, explainer)
    elif st.session_state.role == "Counselor":
        render_counselor_dashboard(model, columns, explainer)
    elif st.session_state.role == "Admin":
        render_admin_dashboard(model, columns)
    else:
        st.error("Unauthorized user role detected.")

    render_footer()


# ==========================================
# ENTRY POINT
# ==========================================
if not st.session_state.authenticated:
    login_screen()
else:
    main_dashboard()