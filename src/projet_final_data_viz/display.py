import streamlit as st
import pandas as pd
from src.projet_final_data_viz.description import describe_dataset
from src.projet_final_data_viz.auth import auth_page
from src.projet_final_data_viz.agents import suggest_graphs, generate_plotly_code
from src.projet_final_data_viz.tapas_code import process_question
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

def display_suggestions (suggestions):
    st.write("\n".join(suggestions))
    graph_list = re.findall(r'\d+\.\s(.*)', suggestions[0])
    return (graph_list if graph_list else ["No suggestions extracted."])

def graph_display(client, df ) : 
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

def user_graph_display(client, df):
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

def display_graph_suggestions(df, client):
    """
    Display suggested graphs based on the dataset and allow users to generate visualizations.
    """
    if "graph_list" not in st.session_state:
        st.subheader("📌 Suggested Graphs")
        suggestions = suggest_graphs(df, client)
        if suggestions:
            st.session_state.graph_list = display_suggestions(suggestions)
        else:
            st.session_state.graph_list = ["No suggestions received."]
    else:
        st.subheader("📌 Suggested Graphs")
        st.write("\n".join(st.session_state.graph_list))
    
    # Graph selection
    if "graph_list" in st.session_state:
        graph_display(client , df)

    
    # User-defined graph suggestion
    user_graph_display(client , df)