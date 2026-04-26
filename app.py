import streamlit as st
import pandas as pd
import fitparse
import plotly.express as px

st.set_page_config(page_title="Diesel Audit", layout="wide")
st.title("🚴‍♂️ The Diesel Audit Dashboard")

uploaded_file = st.file_uploader("Upload .fit file", type='fit')

if uploaded_file:
    with st.spinner("Decoding your ride..."):
        fitfile = fitparse.FitFile(uploaded_file)
        data = []
        for record in fitfile.get_messages('record'):
            r = {data.name: data.value for data in record}
            data.append(r)
        
        df = pd.DataFrame(data)
        df = df.dropna(subset=['power', 'heart_rate'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Big Metrics
    avg_p = df['power'].mean()
    avg_h = df['heart_rate'].mean()
    
    c1, c2 = st.columns(2)
    c1.metric("Avg Power", f"{avg_p:.1f}W")
    c2.metric("Avg Heart Rate", f"{avg_h:.0f}BPM")

    # Decoupling (First half vs Second half)
    mid = len(df) // 2
    ef1 = df.iloc[:mid]['power'].mean() / df.iloc[:mid]['heart_rate'].mean()
    ef2 = df.iloc[mid:]['power'].mean() / df.iloc[mid:]['heart_rate'].mean()
    drift = ((ef1 - ef2) / ef1) * 100
    
    st.subheader(f"Aerobic Decoupling: {drift:.2f}%")
    
    # Visualization
    fig = px.line(df, x='timestamp', y=['power', 'heart_rate'], title="Ride Consistency")
    st.plotly_chart(fig, use_container_width=True)
