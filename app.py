import streamlit as st
import pandas as pd


from description import describe_dataset
from auth import auth_page
from tapas_code import process_question
from claude_code import ask_claude

# Configuration de la page
st.set_page_config(
    page_title="Data Analysis Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé pour centrer le contenu
st.markdown(
    """
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
        .dataframe {
            margin-left: auto;
            margin-right: auto;
        }
        [data-testid="stMetricValue"] {
            justify-content: center;
        }
        [data-testid="stMetricLabel"] {
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Authentification
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False

if not st.session_state['authentication_status']:
    auth_page()
else:
    st.title("📊 Data Analysis Assistant")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            tab1, tab2, tab3 = st.tabs([
                "📈 Dataset Description", "🤖 TAPAS Analysis", "🧠 Claude Analysis"
            ])
            
            with tab1:
                describe_dataset(df)
            
            with tab2:
                st.subheader("Ask TAPAS")
                st.write("\n**Sample Data:**")
                st.dataframe(df.head(), use_container_width=True)
                
                st.write("Example questions:")
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
    
    if st.sidebar.button("Logout"):
        st.session_state['authentication_status'] = False
        st.session_state['claude_api_key'] = None
        st.rerun()
