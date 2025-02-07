import re
import anthropic
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_dataframe(df, max_rows=5, max_features=100):
    """Prépare le dataframe pour minimiser l'usage des tokens avant envoi à Claude."""
    
    #  Sélection des colonnes essentielles
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    text_cols = [col for col in categorical_cols if df[col].str.len().mean() > 20]  # Seuls les textes longs
    
    df_sampled = df.sample(min(max_rows, len(df)))  # Échantillonner quelques lignes

    #  Encodage des variables catégorielles
    for col in categorical_cols:
        df_sampled[col] = LabelEncoder().fit_transform(df_sampled[col].astype(str))

    #  Vectorisation des textes (TF-IDF)
    vectorized_text = {}
    for col in text_cols:
        vectorizer = TfidfVectorizer(max_features=max_features)
        vectorized_text[col] = vectorizer.fit_transform(df_sampled[col].fillna('')).toarray().tolist()

    #  Normalisation des valeurs numériques
    scaler = StandardScaler()
    df_sampled[numeric_cols] = scaler.fit_transform(df_sampled[numeric_cols])

    # Résumé Statistique
    summary_stats = df.describe().to_dict()

    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "summary": summary_stats,
        "sample": df_sampled.to_dict(),
        "vectorized_text": vectorized_text
    }

def ask_claude_optimized(question, df):
    """Envoie la requête optimisée à Claude en limitant l'usage des tokens."""
    if 'claude_api_key' not in st.session_state:
        st.error("API key missing.")
        return "Missing API key."

    client = anthropic.Client(st.session_state.claude_api_key)

    # Prétraitement du DataFrame
    processed_data = preprocess_dataframe(df)

    #  Nettoyage de la question
    question_cleaned = re.sub(r'\s+', ' ', question).strip()

    # Contexte optimisé
    context = f"""
    Dataset Summary:
    - Shape: {processed_data['shape']}
    - Columns: {', '.join(processed_data['columns'])}
    - Sample (Normalized & Encoded): {processed_data['sample']}
    - Text Vectorized: {processed_data['vectorized_text']}

    Question: {question_cleaned}
    """

    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=512,
            temperature=0,
            messages=[{"role": "user", "content": context}]
        )
        return response.content
    except Exception as e:
        st.error(f"Error querying Claude: {e}")
        return "Error getting response."
