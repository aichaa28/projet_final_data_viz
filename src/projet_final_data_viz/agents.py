import pandas as pd
import streamlit as st
import re

# Chemin vers le CSV (uniquement utilisé par load_data() si besoin)
CSV_PATH = "dataset.csv"

def load_data():
    """Charge le fichier CSV et retourne un DataFrame."""
    try:
        df = pd.read_csv(CSV_PATH, dtype=str)
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du CSV : {e}")
        return None



def df_summary(df):
    """Retourne un résumé des colonnes du dataset sous forme de DataFrame."""
    column_summary = []
    for column in df.columns:
        column_info = {
            'Colonne': column,
            'Type de données': str(df[column].dtype),
            'Nombre de valeurs distinctes': df[column].nunique(),
            'Nombre de valeurs manquantes': df[column].isnull().sum(),
            'Nombre de valeurs non manquantes': df[column].notnull().sum(),
            'Exemples de valeurs': [str(v) for v in df[column].dropna().head(5).tolist()]

        }
        column_summary.append(column_info)
    return pd.DataFrame(column_summary)



def suggest_graphs(df, client):
    """
    Envoie une requête à Claude pour analyser le dataset et proposer 5 types
    de graphiques (sans pie charts) sous forme de liste numérotée.
    """
    summary_df = df_summary(df)
    prompt = f"""
    Tu es un expert en visualisation de données. Voici un échantillon de mon jeu de données :
    {df.head(5).to_string()}
    Voici un résumé des colonnes : {summary_df.to_string()}

    Propose 5 types de graphiques intéressants à générer en utilisant Plotly en fonction des colonnes disponibles.
    Les propositions doivent être sous forme de liste numérotée et ne pas utiliser de pie charts.
    Elles doivent être compréhensibles pour des personnes non expertes.
    """
    response = client.messages.create(
        model="claude-2.1",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    if response and isinstance(response.content, list):
        suggestions = [s.text for s in response.content]
    else:
        suggestions = ["Erreur : pas de suggestions reçues."]
    return suggestions

def generate_plotly_code(df, chart_type, client):
    """
    Génère du code Python utilisant Plotly pour créer un graphique correspondant au type sélectionné.
    Le code retourné est brut et doit être exécuté dans un environnement où la dataframe s'appelle df.
    """
    summary_df = df_summary(df)
    prompt = f"""
    Voici un échantillon de mon dataset :
    {df.head(5).to_string()}
    Voici un résumé des colonnes : {summary_df.to_string()}
    Tu devras respecter les bonnes pratiques de la data vizualisation :
    Évitez toute redondance dans la visualisation des bar charts 
    Soit affichez l'axe des y avec des repères indiquant la position des barres, soit optez pour un étiquetage direct en supprimant l'axe des y.
    Par ailleurs, il peut être judicieux de distinguer la barre la plus élevée en lui attribuant une couleur différente,
    Ordonner les barres de manière décroissante lorsque l'ordre de l'axe des x n'est pas indispensable.
    Supprimez également les cadres ou bordures inutiles qui nuisent à l'esthétique. 
    Évitez d'utiliser des bar charts dans des contextes trop complexes.

    Tu dois me donner un code Python représentant un graphique avec Plotly correspondant à "{chart_type}" sans aucune explication.
    Retourne uniquement le code Python de la figure, sans texte supplémentaire sachant que ta dataframe s'appelle df.
    Ne donne que du code brut, prêt à l'utilisation, sans explication !!!
    Entoure le code de crochets.
    """
    response = client.messages.create(
        model="claude-2.1",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    if response and isinstance(response.content, list):
        raw_code = response.content[0].text
    else:
        raw_code = ""
    # Nettoyage du code (suppression éventuelle de balises Markdown)
    code_cleaned = re.sub(r"```python|```", "", raw_code).strip()
    return code_cleaned