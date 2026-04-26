import streamlit as st
import pandas as pd
import fitparse
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Diesel Audit Pro", layout="wide")
st.title("🚴‍♂️ The Diesel Audit: Full Data Explorer")

uploaded_file = st.file_uploader("Upload .fit file", type='fit')

if uploaded_file:
    with st.spinner("Processing full dataset..."):
        fitfile = fitparse.FitFile(uploaded_file)
        data = []
        for record in fitfile.get_messages('record'):
            r = {data.name: data.value for data in record}
            data.append(r)
        
        df = pd.DataFrame(data)
        # Standardize columns
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.dropna(subset=['power', 'heart_rate']).reset_index(drop=True)

    # --- 1. DATA EXPORT SECTION ---
    st.subheader("📥 Data Converter")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Ride Data (CSV)",
        data=csv,
        file_name="diesel_audit_full_data.csv",
        mime="text/csv",
    )

    # --- 2. THE BIG PICTURE ---
    st.subheader("📈 Performance Overview")
    fig = px.line(df, x='timestamp', y=['power', 'heart_rate', 'cadence'], 
                  title="Full Ride Timeline")
    st.plotly_chart(fig, use_container_width=True)

    # --- 3. FATIGUE & STABILITY ANALYSIS ---
    st.subheader("🔍 Fatigue & Technique Audit")
    col1, col2 = st.columns(2)
    
    with col1:
        # Looking for 'sag' in cadence over the 4 hours
        st.write("**Cadence vs. Power (Technique Stability)**")
        fig_cad = px.scatter(df, x='power', y='cadence', color='heart_rate', 
                             opacity=0.5, title="Cadence Distribution")
        st.plotly_chart(fig_cad)

    with col2:
        # Decoupling Calculation
        mid = len(df) // 2
        ef1 = df.iloc[:mid]['power'].mean() / df.iloc[:mid]['heart_rate'].mean()
        ef2 = df.iloc[mid:]['power'].mean() / df.iloc[mid:]['heart_rate'].mean()
        drift = ((ef1 - ef2) / ef1) * 100
        st.write(f"**Aerobic Decoupling: {drift:.2f}%**")
        st.write("This measures how much your efficiency dropped in the second half.")

    # --- 4. RAW DATA TABLE ---
    st.subheader("📑 Every Record (Second-by-Second)")
    st.dataframe(df, use_container_width=True)
