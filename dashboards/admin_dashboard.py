import streamlit as st
import pandas as pd
import numpy as np

def render_admin_dashboard(model, columns):
        
    # System Metrics
    st.markdown("""
    <div class="card">
        <div class="card-header">📊 System Health</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        df = pd.read_csv('data/student-mat.csv', sep=';')
        total = len(df)
        avg_g3 = df['G3'].mean()
        at_risk = len(df[df['G3'] < 10])
        high_perf = len(df[df['G3'] >= 14])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Students", total)
        with col2:
            st.metric("Avg Grade (G3)", f"{avg_g3:.1f}/20")
        with col3:
            st.metric("At-Risk", at_risk, delta=f"{at_risk/total*100:.1f}%")
        with col4:
            st.metric("High Performers", high_perf, delta=f"{high_perf/total*100:.1f}%")
        st.markdown("---")
    except Exception:
        st.info("System metrics unavailable.")

    tab1, tab2 = st.tabs(["User Management", "Batch Predictions"])

    with tab1:
        st.subheader("Registered Users")
        from auth import get_all_users
        users = get_all_users()
        user_df = pd.DataFrame(users, columns=["User ID", "Username", "Role"])
        st.dataframe(user_df, use_container_width=True)

    with tab2:
        st.subheader("Batch Cohort Assessment")
        st.write("Upload a CSV file with student records to get batch predictions.")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.getvalue().decode("utf-8")
                delimiter = ";" if ";" in content else ","
                uploaded_file.seek(0)
                batch_data = pd.read_csv(uploaded_file, sep=delimiter)
                
                # Convert 'yes'/'no' columns to 1/0 — FIXED
                binary_cols = ['schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic']
                for col in binary_cols:
                    if col in batch_data.columns:
                        batch_data[col] = batch_data[col].map({'yes': 1, 'no': 0}).fillna(batch_data[col])
                
                # Handle any remaining string columns
                for col in batch_data.columns:
                    if batch_data[col].dtype == 'object':
                        try:
                            batch_data[col] = pd.to_numeric(batch_data[col], errors='coerce').fillna(0)
                        except:
                            pass
                
                st.write(f"✅ Loaded {len(batch_data)} records")
                
                if st.button("Run Batch Predictions", type="primary"):
                    for col in columns:
                        if col not in batch_data.columns:
                            batch_data[col] = 0
                    
                    batch_inputs = batch_data[columns]
                    preds = model.predict(batch_inputs)
                    batch_data["Predicted_G3"] = np.clip(preds, 1.0, 20.0)
                    
                    st.markdown("---")
                    st.subheader("Batch Results")
                    st.dataframe(batch_data[["Predicted_G3"] + [c for c in columns if c in batch_data.columns]], use_container_width=True)
                    
                    csv = batch_data.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results",
                        data=csv,
                        file_name="batch_predictions.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Error: {str(e)}")