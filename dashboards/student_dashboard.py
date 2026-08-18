import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap

def render_student_dashboard(model, columns, explainer):
    # ===== NO CUSTOM SLIDER CSS — USE STREAMLIT DEFAULTS =====
    
    st.markdown(f"""
    <div class="card">
        <div class="card-header">👋 Welcome, {st.session_state.username}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="card-header">📊 Academic Routine & Behavioral Input</div>
    </div>
    """, unsafe_allow_html=True)

    # ===== SLIDERS WITHOUT KEYS (Let Streamlit handle them) =====
    col1, col2, col3 = st.columns(3)
    with col1:
        studytime = st.slider("Study Time (1-4)", 1, 4, 2)
        failures = st.slider("Past Failures", 0, 4, 0)
        higher = st.selectbox("Higher Education?", ["yes", "no"])
        g1 = st.slider("G1", 0, 20, 10)

    with col2:
        absences = st.slider("Absences", 0, 93, 4)
        health = st.slider("Health (1-5)", 1, 5, 4)
        schoolsup = st.selectbox("School Support?", ["no", "yes"])

    with col3:
        goout = st.slider("Going Out (1-5)", 1, 5, 3)
        internet = st.selectbox("Internet?", ["yes", "no"])
        famsup = st.selectbox("Family Support?", ["yes", "no"])
        g2 = st.slider("G2", 0, 20, 10)

    if st.button("Predict", type="primary"):
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
            "G1": g1,
            "G2": g2
        }

        input_df = pd.DataFrame([payload])[columns]
        prediction = model.predict(input_df)[0]
        prediction_clipped = np.clip(prediction, 1.0, 20.0)

        # Determine risk level
        if prediction_clipped >= 14:
            risk = "Low Risk"
        elif prediction_clipped >= 10:
            risk = "Moderate Risk"
        else:
            risk = "High Risk"

        st.markdown("""
        <div class="card">
            <div class="card-header">📈 Performance Projection</div>
        </div>
        """, unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Predicted Score", f"{prediction_clipped:.2f} / 20")
        with m2:
            if prediction_clipped >= 13:
                st.success("✅ High Achievement")
            elif prediction_clipped >= 10:
                st.warning("📈 Moderate Achievement")
            else:
                st.error("⚠️ At-Risk")

        st.markdown("""
        <div class="card">
            <div class="card-header">🧠 SHAP Explanation</div>
        </div>
        """, unsafe_allow_html=True)
        
        shap_values = explainer(input_df)
        fig, ax = plt.subplots(figsize=(8, 4))
        shap.plots.waterfall(shap_values[0], show=False, max_display=8)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)
        plt.close("all")

        # ===== PDF DOWNLOAD BUTTON =====
                # ===== PDF DOWNLOAD (Single Button) =====
        st.markdown("---")
        st.subheader("📄 Download Report")
        
        from pdf_generator import generate_student_pdf
        pdf_bytes = generate_student_pdf(
            username=st.session_state.username,
            g1=g1,
            g2=g2,
            predicted=prediction_clipped,
            risk=risk,
            studytime=studytime,
            absences=absences,
            failures=failures,
            goout=goout,
            health=health
        )
        st.download_button(
            label="📥 Download My Report (PDF)",
            data=pdf_bytes,
            file_name=f"{st.session_state.username}_report.pdf",
            mime="application/pdf",
            type="secondary"
        )