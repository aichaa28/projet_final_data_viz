
import streamlit as st
import pandas as pd
from auth import auth_page
from tapas_code import process_question
import anthropic

st.set_page_config(page_title="Data Analysis Assistant", layout="wide")  # Must be the first Streamlit command

def describe_dataset(df):
    """Generate dataset description and visualizations"""
    st.subheader("Dataset Overview")
    
    # Basic information
    st.write("**Basic Information:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isna().sum().sum())

    # Data types information
    st.write("\n**Column Types:**")
    col_types = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes,
        'Missing Values': df.isna().sum(),
        'Unique Values': df.nunique()
    })
    st.dataframe(col_types)

    # Sample data
    st.write("\n**Sample Data:**")
    st.dataframe(df.head())

    # Numerical columns analysis
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numerical_cols) > 0:
        st.write("\n**Numerical Columns Analysis:**")
        st.dataframe(df[numerical_cols].describe())



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
    st.title("📊 Data Analysis Assistant")
    
    # File upload
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
                st.dataframe(df.head())
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

    # Add logout button
    if st.sidebar.button("Logout"):
        st.session_state['authentication_status'] = False
        st.session_state['claude_api_key'] = None
        st.rerun()