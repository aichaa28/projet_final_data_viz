# auth.py
import streamlit as st
from transformers import TapasTokenizer, TapasForQuestionAnswering


def auth_page():
    """Page d'authentification"""
    st.title("🔑 Authentification")
    
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False
    
    if not st.session_state['authentication_status']:
        cle_api = st.text_input("Entrez votre clé API Claude :", type="password")
        if st.button("Soumettre"):
            if cle_api:
                st.session_state['claude_api_key'] = cle_api
                try:
                    # Charger le modèle TAPAS
                    st.session_state['tapas_tokenizer'] = TapasTokenizer.from_pretrained('google/tapas-base-finetuned-wtq')
                    st.session_state['tapas_model'] = TapasForQuestionAnswering.from_pretrained('google/tapas-base-finetuned-wtq')
                    st.session_state['authentication_status'] = True
                    st.success("✅ Authentification réussie !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors du chargement du modèle TAPAS : {e}")
            else:
                st.error("Veuillez entrer votre clé API.")

        st.markdown("""
        ### Comment obtenir votre clé API Claude :
        1. Allez sur [Console Anthropic](https://console.anthropic.com/)
        2. Inscrivez-vous ou connectez-vous
        3. Accédez à la section Clés API
        4. Générez une nouvelle clé API
        
        ⚠️ Remarque : Gardez votre clé API en sécurité et ne la partagez jamais publiquement.
        """)
