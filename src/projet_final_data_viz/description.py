import streamlit as st
import pandas as pd
import numpy as np

def describe_dataset(df):
    """Génère une description du jeu de données et affiche des métriques."""
    st.subheader("Aperçu du Jeu de Données")
    
    st.write("**Informations de base :**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Lignes", df.shape[0])
    with col2:
        st.metric("Colonnes", df.shape[1])
    with col3:
        st.metric("Valeurs Manquantes", df.isna().sum().sum())
    with col4:
        st.metric("Doublons", df.duplicated().sum())
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Colonnes Numériques", df.select_dtypes(include=np.number).shape[1])
    with col6:
        st.metric("Colonnes Catégorielles", df.select_dtypes(include=['object', 'category']).shape[1])
    with col7:
        st.metric("Colonnes de Date", df.select_dtypes(include=['datetime64']).shape[1])
    with col8:
        utilisation_memoire = df.memory_usage(deep=True).sum() / 1024**2
        st.metric("Mémoire (MB)", f"{utilisation_memoire:.2f}")
    
    st.write("\n**Types de Colonnes :**")
    types_colonnes = pd.DataFrame({
        'Colonne': df.columns,
        'Type': df.dtypes,
        'Valeurs Manquantes': df.isna().sum(),
        'Valeurs Uniques': df.nunique(),
    })
    st.dataframe(types_colonnes, use_container_width=True)
    
    st.write("\n**Un échantillon de nos Données :**")
    st.dataframe(df.head(), use_container_width=True)
