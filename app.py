import streamlit as st
import pandas as pd
from auth import auth_page
from tapas_code import process_question
import anthropic
import numpy as np 


# Configuration de la page avec mise en page personnalisée
st.set_page_config(
    page_title="Data Analysis Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé pour centrer le contenu
st.markdown("""
    <style>
        .block-container {
            max-width: 1000px;
            padding-top: 2rem;
            padding-bottom: 2rem;
            margin: 0 auto;
        }
        .stButton button {
            margin: 0 auto;
            display: block;
        }
        /* Centre les onglets */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px;
            padding: 0.5rem 1rem;
        }
        /* Centre les tableaux */
        .dataframe {
            margin-left: auto;
            margin-right: auto;
        }
        /* Centre les métriques */
        [data-testid="stMetricValue"] {
            justify-content: center;
        }
        /* Centre le texte des métriques */
        [data-testid="stMetricLabel"] {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

def describe_dataset(df):
    """Generate dataset description and visualizations"""
    st.subheader("Dataset Overview")
    
    # Basic information avec plus de métriques
    st.write("**Basic Information:**")
    
    # Première ligne de métriques
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isna().sum().sum())
    with col4:
        duplicates = df.duplicated().sum()
        st.metric("Duplicates", duplicates)


    # Deuxième ligne de métriques
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        num_cols = df.select_dtypes(include=np.number).columns.size
        st.metric("Numeric Columns", num_cols)
    with col6:
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.size
        st.metric("Categorical Cols", cat_cols)
    with col7:
        date_cols = df.select_dtypes(include=['datetime64']).columns.size
        st.metric("Date Columns", date_cols)
    with col8:
        memory_usage = df.memory_usage(deep=True).sum() / 1024**2  # En MB
        st.metric("Memory (MB)", f"{memory_usage:.2f}")


    # Data types information
    st.write("\n**Column Types:**")
    col_types = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes,
        'Missing Values': df.isna().sum(),
        'Unique Values': df.nunique(),
    })
    st.dataframe(col_types, use_container_width=True)

    # Sample data
    st.write("\n**Sample Data:**")
    st.dataframe(df.head(), use_container_width=True)
    
    
def ask_claude(question, df):
    """Ask question to Claude API"""
    client = anthropic.Client(st.session_state.claude_api_key)
    
    # Prepare context about the dataset
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

# Main application
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False

if not st.session_state['authentication_status']:
    auth_page()
else:
    # Conteneur centré pour le titre
    with st.container():
        st.title("📊 Data Analysis Assistant")
    
    # File upload centré
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["📈 Dataset Description", "🤖 TAPAS Analysis", "🧠 Claude Analysis"])
            
            with tab1:
                describe_dataset(df)
            
            with tab2:
                st.subheader("Ask TAPAS")
                st.write("\n**Sample Data:**")
                # Utiliser toute la largeur pour le tableau
                st.dataframe(df.head(), use_container_width=True)
                
                st.write("Example questions :")
                st.write("• 'What is the sum of [numerical_column]?'")
                st.write("• 'Show the average of [column] by [category]'")
                st.write("• 'List all unique values in [column]'")
                
                tapas_question = st.text_input("Enter your question for TAPAS:")
                if tapas_question:
                    with st.spinner("Processing with TAPAS..."):
                        answer = process_question(tapas_question, df)
                        st.write("🤖 TAPAS Answer:", answer)
            
            with tab3:
                st.subheader("Ask Claude")
                st.write("You can ask Claude more complex questions about the data:")
                st.write("• 'What insights can you provide about this dataset?'")
                st.write("• 'What are the main trends you observe?'")
                st.write("• 'Can you analyze the relationship between X and Y?'")
                
                claude_question = st.text_input("Enter your question for Claude:")
                if claude_question:
                    with st.spinner("Processing with Claude..."):
                        answer = ask_claude(claude_question, df)
                        st.write("🧠 Claude Answer:", answer)
                        
        except Exception as e:
            st.error(f"Error reading file: {e}")

    # Add logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state['authentication_status'] = False
        st.session_state['claude_api_key'] = None
        st.rerun()