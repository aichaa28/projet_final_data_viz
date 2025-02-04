import streamlit as st
from dataviz_claude.api import ask_claude
from dataviz_claude.utils import load_data

st.title("📊 DataViz avec Claude API")

uploaded_file = st.file_uploader("Chargez un fichier CSV", type=["csv"])
if uploaded_file:
    df = load_data(uploaded_file)
    st.write(df.head())

    question = st.text_input("Pose une question sur le dataset")
    if st.button("Analyser avec Claude"):
        prompt = f"Colonnes: {list(df.columns)}. Question: '{question}'"
        st.write("📌 **Claude dit :**", ask_claude(prompt))
