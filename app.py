import streamlit as st
import pandas as pd
from src.projet_final_data_viz.description import describe_dataset
from src.projet_final_data_viz.auth import auth_page
from src.projet_final_data_viz.agents import suggest_graphs, generate_plotly_code, initialize_claude_client
from src.projet_final_data_viz.tapas_code import process_question
from src.projet_final_data_viz.display import setup_page_config, display_suggestions, graph_display, user_graph_display, display_graph_suggestions
import re
import anthropic


def main():
    setup_page_config()
    
    # Vérifier si l'utilisateur est authentifié
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False

    if not st.session_state.get('authentication_status', False):
        auth_page()
        st.stop()  # Arrête l'exécution jusqu'à ce que l'utilisateur soit authentifié

    # Initialisation du client Claude après l'authentification
    client = initialize_claude_client()
    if not client:
        st.error("Failed to initialize Claude API. Please check your API key.")
        st.stop()
    
    st.title("📊 Advanced Data Analysis Assistant")
    
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            tabs = st.tabs(["📈 Dataset Analysis", "🤖 TAPAS Query Engine", "📊 Advanced Visualization"])
            
            with tabs[0]:
                describe_dataset(df)
            
            with tabs[1]:
                st.subheader("TAPAS Query Engine")
                st.dataframe(df.head(), use_container_width=True)
                
                st.markdown("""
                    **Example Queries:**
                    - Calculate sum of numeric columns
                    - Show average values by category
                    - Find unique values in columns
                """)
                
                query = st.text_input("Enter your data query:")
                if query:
                    with st.spinner("Processing query..."):
                        result = process_question(query, df)
                        st.success(f"Query Result: {result}")
            
            with tabs[2]:
                display_graph_suggestions(df,client)
                
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
    else:
        st.info("Please upload a CSV file to begin analysis")
    
    if st.sidebar.button("Sign Out"):
        st.session_state['authentication_status'] = False
        st.session_state['claude_api_key'] = None
        st.session_state.pop('claude_client', None)
        st.rerun()

if __name__ == "__main__":
    main()