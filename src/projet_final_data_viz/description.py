import streamlit as st
import pandas as pd
import numpy as np

def describe_dataset(df):
    """Génère une description du dataset et affiche des métriques."""
    st.subheader("Dataset Overview")
    
    st.write("**Basic Information:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isna().sum().sum())
    with col4:
        st.metric("Duplicates", df.duplicated().sum())
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Numeric Columns", df.select_dtypes(include=np.number).shape[1])
    with col6:
        st.metric("Categorical Cols", df.select_dtypes(include=['object', 'category']).shape[1])
    with col7:
        st.metric("Date Columns", df.select_dtypes(include=['datetime64']).shape[1])
    with col8:
        memory_usage = df.memory_usage(deep=True).sum() / 1024**2
        st.metric("Memory (MB)", f"{memory_usage:.2f}")
    
    st.write("\n**Column Types:**")
    col_types = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes,
        'Missing Values': df.isna().sum(),
        'Unique Values': df.nunique(),
    })
    st.dataframe(col_types, use_container_width=True)
    
    st.write("\n**Sample Data:**")
    st.dataframe(df.head(), use_container_width=True)

