import pandas as pd
import streamlit as st
import anthropic
import numpy as np


def limit_fig_json_length(fig, max_length=5000):
    # Convertir la figure en JSON
    fig_json = fig.to_json()

    # Vérifier la longueur du JSON
    if len(fig_json) > max_length:
        # Si la longueur dépasse la limite, couper la chaîne et ajouter un message
        truncated_json = fig_json[:max_length] + "... (truncated)"
        return truncated_json
    else:
        return fig_json

def initialize_claude_client():
    """Initialize the Claude API client using the user's provided API key."""
    if 'claude_client' not in st.session_state:
        api_key = st.session_state.get('claude_api_key')  # Récupère la clé API saisie par l'utilisateur

        if api_key:
            try:
                st.session_state.claude_client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                st.error(f"Error initializing Claude client: {e}")
                return None
        else:
            st.error("Claude API key not found. Please enter your API key in the authentication page.")
            return None

    return st.session_state.claude_client


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

    Propose 5 types de graphiques intéressants à générer en utilisant Plotly en fonction des colonnes disponibles dans {df}.
    Les propositions doivent être sous forme de liste numérotée et ne pas utiliser de pie charts.
    Elles doivent être compréhensibles pour des personnes non expertes.
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
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
    Évitez toute redondance dans la visualisation des bar charts :
    -Soit affichez l'axe des y avec des repères indiquant la position des barres 
    -soit optez pour un étiquetage direct en supprimant l'axe des y.
    Par ailleurs, il peut être judicieux de distinguer la barre la plus élevée en lui attribuant une couleur différente,
    Ordonner les barres de manière décroissante lorsque l'ordre de l'axe des x n'est pas indispensable.
    Supprimez également les cadres ou bordures inutiles qui nuisent à l'esthétique. 
    Évitez d'utiliser des bar charts dans des contextes trop complexes.

    Tu dois me donner un code Python représentant un graphique avec Plotly correspondant à "{chart_type}" sans aucune explication.
    Retourne uniquement le code Python de la figure, sans texte supplémentaire sachant que ta dataframe s'appelle df.
    Ne donne que du code brut, prêt à l'utilisation, sans explication !!!
    Entoure le code de crochets !
    N'oublies pas d'eviter ces erreur :
    -❌ Error executing the code: 'Figure' object has no attribute 'update_xaxis' 
    -❌ Error executing the code: 'Figure' object has no attribute 'update_yaxis
    Exemple : [ sales_by_category = df.groupby('x')['y'].sum().reset_index()

    fig = px.bar(sales_by_category, x='x', y='y', 
             title="Somme des Valeurs par Catégorie")]
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    if response and isinstance(response.content, list):
        raw_code = response.content[0].text
        print(raw_code)
    else:
        raw_code = ""
    # Encadrer le code retourné avec des crochets
    final_code = f"[{raw_code}]"
    
    return final_code


def interpret_fig(fig, client):
    """
    Améliore l'interprétation du graphique en extrayant des statistiques clés avant de les envoyer à Claude.
    Si le graphique n'a pas d'axes X et Y (ex: Sankey), il envoie uniquement le JSON.
    """
    try:
        # Convertir la figure en JSON
        fig_json = limit_fig_json_length(fig, max_length=10000)

        # Récupérer le titre du graphique et le type de graphique
        fig_title = fig.layout.title.text if fig.layout.title else 'Aucun titre'
        fig_type = fig.__class__.__name__

        # Vérifier si le graphique a des données X et Y
        data = fig.data[0]  # On prend la première série de données
        has_axes = hasattr(data, "x") and hasattr(data, "y")

        if has_axes:
            # Extraction des données numériques (si disponibles)
            np.array(pd.to_numeric(data.x, errors='coerce'))
            y_values = np.array(pd.to_numeric(data.y, errors='coerce'))

            # Filtrer les valeurs manquantes (NaN) dans y_values
            y_values_clean = y_values[~np.isnan(y_values)]  # Retirer les NaN

            # Vérifier si des valeurs sont présentes après nettoyage
            if y_values_clean.size > 0:
                # Calcul des statistiques principales
                min_y = np.nanmin(y_values_clean)
                max_y = np.nanmax(y_values_clean)
                mean_y = np.nanmean(y_values_clean)
                median_y = np.nanmedian(y_values_clean)
                std_y = np.nanstd(y_values_clean)

                prompt = f"""
                Tu es un expert en visualisation de données. Voici une analyse d'un graphique.

                **Titre du graphique :** {fig_title}
                **Type de graphique :** {fig_type}

                **Statistiques clés :**
                - Valeur minimale : {min_y:.2f}
                - Valeur maximale : {max_y:.2f}
                - Moyenne : {mean_y:.2f}
                - Médiane : {median_y:.2f}
                - Écart-type : {std_y:.2f}

                **Axes :**
                - Axe X : {data.xaxis if hasattr(data, 'xaxis') else 'Inconnu'}
                - Axe Y : {data.yaxis if hasattr(data, 'yaxis') else 'Inconnu'}

                **Analyse demandée :**
                1️⃣ **Décris les tendances générales s'il y en a besoin.**  
                2️⃣ **Lorsque tu parles de valeurs, précise à quel attribut elles appartiennent.**  
                3️⃣ **Fournis une conclusion synthétique en 3 à 5 phrases pour un décideur.**  

                Tout cela en 10 lignes maximum 
                JSON du graphique :
                {fig_json}
                """
            else:
                prompt = f"""
                Tu es un expert en visualisation de données. Voici une analyse d'un graphique.

                **Titre du graphique :** {fig_title}
                **Type de graphique :** {fig_type}

                Les valeurs Y sont absentes ou non numériques. Veuillez vérifier les données et ajuster l'analyse en conséquence.

                Tout cela en 10 lignes maximum
                JSON du graphique :
                {fig_json}
                """
        else:
            # Cas où le graphique n'a pas d'axes (ex: Sankey)
            prompt = f"""
            Tu es un expert en visualisation de données. Voici un graphique complexe sans axes classiques.

            **Titre du graphique :** {fig_title}
            **Type de graphique :** {fig_type}

            - Ce graphique ne contient pas de valeurs X et Y classiques.  
            - Analyse directement la structure JSON pour en déduire une interprétation pertinente.  
            - Décris les relations clés, la signification des nœuds et liens, et l'idée principale du graphique. 

            Tout cela en 10 lignes maximum

            JSON du graphique :
            {fig_json}
            """

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        interpretation = response.content[0].text if response and isinstance(response.content, list) else "Erreur d'interprétation."

    except Exception as e:
        interpretation = f"Erreur lors du traitement : {e}"

    return interpretation





def display_fig_interpretation(fig, client):
    """Affiche dans Streamlit l'interprétation du graphique."""
    st.subheader("Interprétation du graphique")
    interpretation = interpret_fig(fig, client)
    st.write(interpretation)