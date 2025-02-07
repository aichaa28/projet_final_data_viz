import streamlit as st
import pandas as pd
from description import describe_dataset
from auth import auth_page
from agents import suggest_graphs, generate_plotly_code
from tapas_code import process_question
import re
import anthropic

def setup_page_config():
    st.set_page_config(
        page_title="Data Analysis Assistant",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.markdown("""
        <style>
            .block-container {
                max-width: 1200px;
                padding: 2rem;
                margin: 0 auto;
            }
            .stButton button {
                margin: 0 auto;
                display: block;
                background-color: #4CAF50;
                color: white;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 2rem;
                justify-content: center;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #f8f9fa;
                border-radius: 4px;
                padding: 0.5rem 1rem;
            }
            .dataframe {
                margin: 0 auto;
            }
            [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)


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


def display_graph_suggestions(df, client):
    """
    Display suggested graphs based on the dataset and allow users to generate visualizations.
    """
    if "graph_list" not in st.session_state:
        st.subheader("📌 Suggested Graphs")
        suggestions = suggest_graphs(df, client)
        if suggestions:
            st.write("\n".join(suggestions))
            graph_list = re.findall(r'\d+\.\s(.*)', suggestions[0])
            st.session_state.graph_list = graph_list if graph_list else ["No suggestions extracted."]
        else:
            st.session_state.graph_list = ["No suggestions received."]
    else:
        st.subheader("📌 Suggested Graphs")
        st.write("\n".join(st.session_state.graph_list))
    
    # Graph selection
    if "graph_list" in st.session_state:
        st.subheader("Visualization")
        selected_graph = st.selectbox("Choose a graph type:", st.session_state.graph_list)
        if st.button("Generate Graph"):
            with st.spinner("Generating..."):
                plotly_code = generate_plotly_code(df, selected_graph, client).strip()
                match = re.search(r"\[(.*?)\]", plotly_code, re.DOTALL)
                x_code = match.group(1).strip() if match else ""
                st.code(x_code, language="python")
                
                if x_code:
                    try:
                        local_vars = {}
                        exec(x_code, globals(), local_vars)
                        fig = local_vars.get("fig")
                        if fig:
                            st.plotly_chart(fig)
                        else:
                            st.error("❌ Error: 'fig' was not generated.")
                    except Exception as e:
                        st.error(f"Error executing the code: {e}")
                else:
                    st.error("❌ No valid code returned by Claude.")
    
    # User-defined graph suggestion
    st.subheader("Suggest a Graph:")
    question = st.text_input("Graph Suggestion:")
    if st.button("Generate Your Graph"):
        with st.spinner("Generating..."):
            plotly_code = generate_plotly_code(df, question, client).strip()
            match = re.search(r"\[(.*?)\]", plotly_code, re.DOTALL)
            x_code2 = match.group(1).strip() if match else ""
            st.code(x_code2, language="python")
            
            if x_code2:
                try:
                    local_vars = {}
                    exec(x_code2, globals(), local_vars)
                    fig = local_vars.get("fig")
                    if fig:
                        st.plotly_chart(fig)
                    else:
                        st.error("❌ Error: 'fig' was not generated.")
                except Exception as e:
                    st.error(f"Error executing the code: {e}")
            else:
                st.error("❌ No valid code returned by Claude.")

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