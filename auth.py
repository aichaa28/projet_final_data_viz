import streamlit as st

def auth_page():
    st.title("🔑 Authentification")

    api_key = st.text_input("Entrez votre clé API Claude :", type="password")

    if st.button("Valider"):
        if api_key:
            # Stocker la clé API dans la session
            st.session_state["claude_api_key"] = api_key
            st.success("Clé API enregistrée avec succès !")
            st.rerun()  # Recharger la page pour passer à l'application principale
        else:
            st.error("Veuillez entrer une clé API valide.")

