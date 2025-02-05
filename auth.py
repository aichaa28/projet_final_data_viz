import streamlit as st


def auth_page():
    st.title("🔑 Authentication")

    api_key = st.text_input("Enter your Claude API key:", type="password")

    if st.button("Submit"):
        if api_key:
            # Stocker la clé API dans la session
            st.session_state['claude_api_key'] = api_key
            st.success("API key successfully saved!")
        else:
            st.error("Please enter a valid API key.")


