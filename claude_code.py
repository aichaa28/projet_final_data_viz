import streamlit as st
import anthropic as anthropic

@st.cache
def ask_claude(question, df):
    """Envoie une question à l'API Claude et retourne la réponse."""
    client = anthropic.Client(st.session_state.claude_api_key)
    context = f"""Here is information about the dataset:
    - Shape: {df.shape}
    - Columns: {', '.join(df.columns)}
    - Sample data:\n{df.head().to_string()}
    
    Question: {question}
    
    Please provide a clear and concise answer based on the data provided."""
    
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            temperature=0,
            messages=[{"role": "user", "content": context}]
        )
        return response.content
    except Exception as e:
        st.error(f"Error querying Claude: {e}")
        return "Error getting response from Claude"
