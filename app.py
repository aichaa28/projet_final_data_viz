import streamlit as st
import pandas as pd
from src.projet_final_data_viz.description import describe_dataset
from src.projet_final_data_viz.auth import auth_page
from src.projet_final_data_viz.agents import initialize_claude_client, suggest_graphs
from src.projet_final_data_viz.tapas_code import process_question
from src.projet_final_data_viz.display import setup_page_config, user_graph_display, graph_display, display_suggestions

def main():
    setup_page_config()

    # Vérifier si l'utilisateur est authentifié
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False

    if not st.session_state.get('authentication_status', False):
        auth_page()
        st.stop()

    # Initialisation du client Claude après l'authentification
    client = initialize_claude_client()
    if not client:
        st.error("Échec de l'initialisation de l'API Claude. Veuillez vérifier votre clé API.")
        st.stop()

    st.title("📊 Assistant Graphique Intelligent")

    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("📂 Télécharger un fichier CSV", type=["csv"])

    if uploaded_file:
        file_id = uploaded_file.name  # Identifiant unique pour le fichier

        # Vérifier si le fichier a changé
        if 'uploaded_file_id' not in st.session_state or st.session_state.uploaded_file_id != file_id:
            st.session_state.uploaded_file_id = file_id  # Met à jour l'ID du fichier
            st.session_state.df = pd.read_csv(uploaded_file)

            # Réinitialiser les suggestions et la liste des graphes
            st.session_state.graph_list = None
            st.session_state.suggestions = None

        try:
            if st.session_state.suggestions is None:
                st.session_state.suggestions = suggest_graphs(st.session_state.df, client)

            tabs = st.tabs(["📈 Analyse du Jeu de Données", "🤖 Moteur de Requêtes TAPAS", "📊 Visualisation Avancée", "💡 Suggérer un Graphe"])

            with tabs[0]:
                describe_dataset(st.session_state.df)

            with tabs[1]:
                st.subheader("Moteur de Requêtes TAPAS")
                st.dataframe(st.session_state.df.head(), use_container_width=True)
                st.markdown(
                """
                **📝 Remarque sur TAPAS :**  
                - TAPAS fonctionne **beaucoup plus rapidement** et est **plus performant** sur des petits jeux de données.  
                - Il accepte les **questions uniquement en anglais**.  
                """
                )
                with st.expander("Cliquez pour voir des exemples de requêtes :"):
                    st.markdown(
                        """
                        **💡 Example Queries:**  
                        - **Calculate the sum of `[numerical column]`**  
                        - **What is the sum of `[numerical column]` by `[column]`?**  
                        - **Find unique values in column**  
                        - **Display the average of a specific column**  
                 
                        """
                    )


                query = st.text_input("Entrez votre requête de données :")
                if query:
                    with st.spinner("Traitement de la requête..."):
                        result = process_question(query, st.session_state.df)
                        st.success(f"Résultat de la requête : {result}")

            with tabs[2]:
                st.markdown("⚠️ En cas d'erreur, n'hésitez pas à recharger le graphique.")
                if st.session_state.graph_list is None:
                    st.subheader("📌 Graphes Suggérés")
                    st.session_state.graph_list = display_suggestions(st.session_state.suggestions)
                    
                graph_display(client, st.session_state.df)

            with tabs[3]:
                st.subheader("📌 Suggestions de Graphes Définies par l'Utilisateur")
                user_graph_display(client, st.session_state.df)

        except Exception as e:
            st.error(f"Erreur lors du traitement des données : {str(e)}")

    else:
        st.info("Veuillez télécharger un fichier CSV pour commencer l'analyse")

    if st.sidebar.button("Se Déconnecter"):
        st.session_state['authentication_status'] = False
        st.session_state['claude_api_key'] = None
        st.session_state.pop('claude_client', None)
        st.rerun()

if __name__ == "__main__":
    main()
