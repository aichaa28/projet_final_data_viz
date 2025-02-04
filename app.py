import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from dotenv import load_dotenv
from auth import auth_page

# Load environment variables
load_dotenv()
CLAUDE_API_URL = "https://api.anthropic.com/v1/complete"


def ask_claude(question, dataset_summary):
    headers = {
        "Authorization": f"Bearer {st.session_state.claude_api_key}",
        "Content-Type": "application/json"
    }
    prompt = """Here is a summary of
    a dataset: {dataset_summary}. Answer the question: {question}"""
    data = {"prompt": prompt, "max_tokens": 200}
    response = requests.post(CLAUDE_API_URL, json=data, headers=headers)
    return response.json().get("completion", "No answer found")


def generate_visualizations(df, question): 
    # Function to generate visualizations
    if "distribution" in question.lower():
        col = df.select_dtypes(include=['number']).columns[0]
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(df[col], kde=True, ax=ax)
        st.pyplot(fig)
    elif "correlation" in question.lower():
        fig = px.imshow(df.corr(), text_auto=True)
        st.plotly_chart(fig)
    elif "relationship" in question.lower():
        if len(df.select_dtypes(include=['number']).columns) >= 2:
            fig = px.scatter(df, x=df.columns[0], y=df.columns[1])
            st.plotly_chart(fig)
        else:
            st.warning("Not enough numeric columns to show a relationship.")
    else:
        st.warning("No visualization available for this question.")


def show_describe_graphs(df):
    # Function to show descriptive statistics in graphs
    st.subheader("📊 Descriptive Statistics (Graphs)")
    numeric_cols = df.select_dtypes(include=['number']).columns
    numeric_cols = numeric_cols.dropna()
    if len(numeric_cols) == 0:
        st.warning("No numeric columns found.")
        return

    selected_col = st.selectbox("Choose a numeric column:", numeric_cols)
    stats = df[selected_col].describe().sort_values(ascending=False)

    st.write(f"#### Statistics for column: {selected_col}")

    # Graph 1: Mean, Standard deviation, Min, Max
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    bars = sns.barplot(
    x=stats.index[1:],
    y=stats.values[1:],
    ax=ax1,
    palette="viridis"
)
    for container in bars.containers:
        ax1.bar_label(container, fmt='%.2f', padding=3)

    sns.despine(left=True)
    ax1.set_yticks([])
    ax1.set_ylabel('')
    st.pyplot(fig1)

    # Graph 2: Boxplot
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.boxplot(x=df[selected_col], ax=ax2, color="skyblue")
    sns.despine(left=True)
    ax2.set_yticks([])
    ax2.set_ylabel('')
    st.pyplot(fig2)


# Function to show categorical column statistics
def show_categorical_graphs(df):
    st.subheader("📊 Descriptive Statistics for Categorical Columns")
    
    # Identifying categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    if len(categorical_cols) == 0:
        st.warning("No categorical columns found.")
        return

    # Select the column to analyze
    selected_col = st.selectbox("Choose a categorical column:", categorical_cols)
    
    # Calculating frequencies
    value_counts = df[selected_col].value_counts()

    st.write(f"#### Frequencies for column: {selected_col}")

    # Graph: Distribution of categories
    fig, ax = plt.subplots(figsize=(8, 4))
    top_5 = value_counts.head(5)
    sns.barplot(x=top_5.index, y=top_5.values, ax=ax, color="skyblue")  # Uniform color

    # Add direct labels
    for i, value in enumerate(top_5.values):
        ax.text(i, value + 0.05, f'{value:.2f}', ha='center', va='bottom', fontsize=10)

    # Customize labels and title
    ax.set_xlabel(selected_col)
    ax.set_ylabel('Frequency')
    ax.set_title(f'Distribution of Top Categories in {selected_col}')

    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    ax.get_yaxis().set_visible(False)
    # Remove left spine for cleaner look
    sns.despine(left=True)

    # Display the plot
    st.pyplot(fig)


def describe_dataset(df):
    # Function to describe the dataset
    missing_values = df.isnull().sum()

    # Filtrer les colonnes avec plus de 0 valeurs manquantes
    missing_values = missing_values[missing_values > 0]
    st.subheader("📊 Dataset Description")
    st.write("**Data preview:**", df.head())
    st.write("**Missing values by column:**", missing_values.nlargest(5))
    show_describe_graphs(df)
    show_categorical_graphs(df)


if "claude_api_key" not in st.session_state:
    # Show the authentication page if the API key is not set
    auth_page()
else:
    # Show the main application if the API key is set
    st.title("📊 DataViz with Claude AI")

    # Dataset upload
    uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        num_rows, num_columns = df.shape

        # Nombre de colonnes numériques et catégorielles
        num_numeric = df.select_dtypes(include=['number']).shape[1]
        num_categorical = df.select_dtypes(include=['object']).shape[1]

        # Affichage des informations
        st.write(f"**Number of rows:** {num_rows}")
        st.write(f"**Number of columns:** {num_columns}")
        st.write(f"**Numerical columns:** {num_numeric}")
        st.write(f"**Categorical columns:** {num_categorical}")
        describe_dataset(df)

        st.subheader("Ask a question or choose a suggestion:")
        question = st.text_input("Ask a question about the dataset:")

        suggested_questions = [
            "What is the distribution of the first numeric column?",
            "Is there a correlation between the numeric columns?",
            "What is the relationship between the first two numeric columns?"
        ]
        selected_question = st.selectbox("Or choose a suggested question:", suggested_questions)

        if st.button("Get the answer"):
            final_question = question if question else selected_question
            if final_question:
                dataset_summary = str(df.describe())
                answer = ask_claude(final_question, dataset_summary)
                st.write("🧠 Claude's answer:", answer)
                generate_visualizations(df, final_question)
            else:
                st.warning("Please enter a question.")
