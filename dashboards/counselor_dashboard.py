import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap

# This is the function name app.py is looking for
def render_counselor_dashboard(model, columns, explainer):
    st.markdown("""
    <div class="card">
        <div class="card-header">🎯 Risk Triage & Behavioral Simulator</div>
        <p style="color: #64748B; font-size: 14px; margin: 0;">
            Predict student outcomes and run what-if scenarios.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Student Selector — NO G3
    st.markdown("""
    <div class="card">
        <div class="card-header">👤 Select Student for Consultation</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        df_students = pd.read_csv('data/student-mat.csv', sep=';')
        df_students['student_id'] = df_students.index
        
        student_options = df_students.apply(
            lambda row: f"ID {row['student_id']} | G1: {row['G1']} | G2: {row['G2']}", 
            axis=1
        ).tolist()
        
        selected_idx = st.selectbox(
            "Select Student to Counsel", 
            range(len(student_options)),
            format_func=lambda i: student_options[i]
        )
        
        student_data = df_students.iloc[selected_idx]
        
        st.info(f"""
        **Selected Student Profile:**
        - **G1 (Term 1):** {student_data['G1']}/20
        - **G2 (Term 2):** {student_data['G2']}/20
        - **Absences:** {student_data['absences']}
        - **Study Time:** {student_data['studytime']}
        - **Failures:** {student_data['failures']}
        """)
        st.markdown("---")
        
        default_study = student_data['studytime']
        default_fail = student_data['failures']
        default_abs = student_data['absences']
        default_health = student_data['health']
        default_goout = student_data['goout']
        default_higher = "yes" if student_data['higher'] == 1 else "no"
        default_schoolsup = "yes" if student_data['schoolsup'] == 1 else "no"
        default_famsup = "yes" if student_data['famsup'] == 1 else "no"
        default_internet = "yes" if student_data['internet'] == 1 else "no"
        default_g1 = student_data['G1']
        default_g2 = student_data['G2']
        
    except Exception as e:
        st.warning(f"Could not load student data: {e}. Using manual input mode.")
        default_study = 2
        default_fail = 0
        default_abs = 4
        default_health = 4
        default_goout = 3
        default_higher = "yes"
        default_schoolsup = "no"
        default_famsup = "yes"
        default_internet = "yes"
        default_g1 = 10
        default_g2 = 10

    tab1, tab2 = st.tabs(["Individual Student Diagnostic", "What-If Scenario Simulator"])

    with tab1:
        st.markdown("""
        <div class="card">
            <div class="card-header">📝 Student Behavioral Profile</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            studytime = st.slider("Study Time (1-4)", 1, 4, default_study, key="c_study")
            failures = st.slider("Past Failures", 0, 4, default_fail, key="c_fail")
            higher = st.selectbox("Higher Education?", ["yes", "no"], key="c_high", index=0 if default_higher == "yes" else 1)
            g1 = st.slider("G1", 0, 20, default_g1, key="c_g1")

        with col2:
            absences = st.slider("Absences", 0, 93, default_abs, key="c_abs")
            health = st.slider("Health (1-5)", 1, 5, default_health, key="c_health")
            schoolsup = st.selectbox("School Support?", ["no", "yes"], key="c_supp", index=0 if default_schoolsup == "no" else 1)

        with col3:
            goout = st.slider("Going Out (1-5)", 1, 5, default_goout, key="c_goout")
            famsup = st.selectbox("Family Support?", ["yes", "no"], key="c_famsup", index=0 if default_famsup == "yes" else 1)
            internet = st.selectbox("Internet?", ["yes", "no"], key="c_net", index=0 if default_internet == "yes" else 1)
            g2 = st.slider("G2", 0, 20, default_g2, key="c_g2")

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

            st.markdown("---")
            st.subheader("📈 Diagnostic Result")
            
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Predicted Final Score", f"{prediction_clipped:.2f} / 20")
            with m2:
                if prediction_clipped >= 13:
                    st.success("✅ Low Risk")
                elif prediction_clipped >= 10:
                    st.warning("📈 Moderate Risk")
                else:
                    st.error("⚠️ High Risk (Intervention Required)")

            st.markdown("---")
            st.subheader("🧠 SHAP Explanation")
            
            shap_values = explainer(input_df)
            fig, ax = plt.subplots(figsize=(8, 4))
            shap.plots.waterfall(shap_values[0], show=False, max_display=8)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)
            plt.close("all")

            st.markdown("---")
            st.subheader("📋 Intervention Log")
            
            risk_factors = []
            if absences > 5:
                risk_factors.append("High Absences")
            if studytime < 3:
                risk_factors.append("Low Study Time")
            if goout >= 4:
                risk_factors.append("High Outings")
            if failures > 1:
                risk_factors.append("Past Failures")
            if g1 < 10:
                risk_factors.append("Low G1")
            if g2 < 10:
                risk_factors.append("Low G2")
            
            risk_text = ", ".join(risk_factors) if risk_factors else "None identified"
            
            notes = f"""=== ACADEMIC ADVISING SESSION ===
• Student ID: {selected_idx if 'selected_idx' in locals() else 'N/A'}
• G1: {g1} | G2: {g2} | Predicted G3: {prediction_clipped:.2f}
• Failures: {failures} | Absences: {absences} | Study Time: {studytime}
• Risk Factors: {risk_text}
• Action Plan: 
  - Increase study hours to Level {min(4, studytime+1)}
  - Monitor attendance
  - {'Follow-up in 2 weeks' if prediction_clipped < 10 else 'Check-in next month'}
"""
            st.code(notes, language="text")

            # ===== PDF DOWNLOAD BUTTON (Counselor) =====
            # ===== PDF DOWNLOAD (Single Button) =====
            st.markdown("---")
            st.subheader("📄 Download Report")
            
            from pdf_generator import generate_counselor_pdf
            
            action_plan = f"""- Increase study hours to Level {min(4, studytime+1)}
- Monitor attendance
- {'Follow-up in 2 weeks' if prediction_clipped < 10 else 'Check-in next month'}"""
            
            pdf_bytes = generate_counselor_pdf(
                username=f"Student ID: {selected_idx if 'selected_idx' in locals() else 'N/A'}",
                g1=g1,
                g2=g2,
                predicted=prediction_clipped,
                risk=risk,
                studytime=studytime,
                absences=absences,
                failures=failures,
                goout=goout,
                health=health,
                risk_factors=risk_text,
                action_plan=action_plan
            )
            st.download_button(
                label="📥 Download Student Report (PDF)",
                data=pdf_bytes,
                file_name=f"student_{selected_idx if 'selected_idx' in locals() else 'N/A'}_report.pdf",
                mime="application/pdf",
                type="secondary"
            )
            
    with tab2:
        st.markdown("""
        <div class="card">
            <div class="card-header">🔄 What-If Scenario Simulator</div>
            <p style="color: #64748B; font-size: 14px; margin: 0;">
                Compare current vs improved habits to see potential score gains.
            </p>
        </div>
        """, unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("#### Current Profile")
            curr_study = st.slider("Study Time", 1, 4, default_study if 'default_study' in locals() else 2, key="sim_cstudy")
            curr_abs = st.slider("Absences", 0, 50, default_abs if 'default_abs' in locals() else 10, key="sim_cabs")
            curr_goout = st.slider("Going Out", 1, 5, default_goout if 'default_goout' in locals() else 3, key="sim_cgo")
            curr_fail = st.slider("Past Failures", 0, 4, default_fail if 'default_fail' in locals() else 1, key="sim_cfail")
            curr_g1 = st.slider("G1", 0, 20, default_g1 if 'default_g1' in locals() else 10, key="sim_cg1")
            curr_g2 = st.slider("G2", 0, 20, default_g2 if 'default_g2' in locals() else 10, key="sim_cg2")

        with sc2:
            st.markdown("#### Target Goals")
            targ_study = st.slider("Study Time", 1, 4, min(4, (default_study if 'default_study' in locals() else 2) + 1), key="sim_tstudy")
            targ_abs = st.slider("Absences", 0, 50, max(0, (default_abs if 'default_abs' in locals() else 10) - 3), key="sim_tabs")
            targ_goout = st.slider("Going Out", 1, 5, max(1, (default_goout if 'default_goout' in locals() else 3) - 1), key="sim_tgo")
            targ_fail = st.slider("Past Failures", 0, 4, max(0, (default_fail if 'default_fail' in locals() else 1) - 1), key="sim_tfail")
            targ_g1 = st.slider("G1", 0, 20, min(20, (default_g1 if 'default_g1' in locals() else 10) + 2), key="sim_tg1")
            targ_g2 = st.slider("G2", 0, 20, min(20, (default_g2 if 'default_g2' in locals() else 10) + 2), key="sim_tg2")

        if st.button("Simulate Impact", type="primary"):
            curr_payload = {
                "studytime": curr_study, "failures": curr_fail, "absences": curr_abs, 
                "health": 3, "goout": curr_goout, "freetime": 3, "Dalc": 1, "Walc": 1, 
                "famrel": 4, "Medu": 3, "Fedu": 3, "schoolsup": 0, "famsup": 1, 
                "higher": 1, "internet": 1, "G1": curr_g1, "G2": curr_g2
            }
            targ_payload = {
                "studytime": targ_study, "failures": targ_fail, "absences": targ_abs, 
                "health": 3, "goout": targ_goout, "freetime": 3, "Dalc": 1, "Walc": 1, 
                "famrel": 4, "Medu": 3, "Fedu": 3, "schoolsup": 0, "famsup": 1, 
                "higher": 1, "internet": 1, "G1": targ_g1, "G2": targ_g2
            }

            p_curr = np.clip(model.predict(pd.DataFrame([curr_payload])[columns])[0], 1.0, 20.0)
            p_targ = np.clip(model.predict(pd.DataFrame([targ_payload])[columns])[0], 1.0, 20.0)
            diff = p_targ - p_curr

            st.markdown("---")
            res1, res2, res3 = st.columns(3)
            with res1:
                st.metric("Current Score", f"{p_curr:.2f} / 20")
            with res2:
                st.metric("Target Score", f"{p_targ:.2f} / 20")
            with res3:
                st.metric("Potential Gain", f"+{diff:.2f} pts", delta_color="normal")
            
            st.info(f"""
            **Summary:**
            - Study: {curr_study} → {targ_study}
            - Absences: {curr_abs} → {targ_abs}
            - G1: {curr_g1} → {targ_g1}
            - G2: {curr_g2} → {targ_g2}
            - **Improvement: +{diff:.2f} points**
            """)