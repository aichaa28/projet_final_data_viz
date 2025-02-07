# auth.py
import streamlit as st
from transformers import TapasTokenizer, TapasForQuestionAnswering

def auth_page():
    """Authentication page"""
    st.title("🔑 Authentication")
    
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False
    
    if not st.session_state['authentication_status']:
        api_key = st.text_input("Enter your Claude API key:", type="password")
        if st.button("Submit"):
            if api_key:
                st.session_state['claude_api_key'] = api_key
                try:
                    # Load TAPAS model
                    st.session_state['tapas_tokenizer'] = TapasTokenizer.from_pretrained('google/tapas-base-finetuned-wtq')
                    st.session_state['tapas_model'] = TapasForQuestionAnswering.from_pretrained('google/tapas-base-finetuned-wtq')
                    st.session_state['authentication_status'] = True
                    st.success("✅ Authentication successful!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading TAPAS model: {e}")
            else:
                st.error("Please enter your API key.")

        st.markdown("""
        ### How to get your Claude API key:
        1. Go to [Anthropic Console](https://console.anthropic.com/)
        2. Sign up or log in
        3. Navigate to API Keys
        4. Generate a new API key
        
        ⚠️ Note: Keep your API key secure and never share it publicly.
        """)