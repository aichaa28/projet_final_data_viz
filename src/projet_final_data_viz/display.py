import streamlit as st
from src.projet_final_data_viz.agents import suggest_graphs, generate_plotly_code, interpret_fig
import re
import plotly.express as px
import plotly.graph_objects as go

def setup_page_config():
    st.set_page_config(
        page_title="Assistant Graphique Intelligent",
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


def display_suggestions(suggestions):
    st.write("\n".join(suggestions))
    graph_list = re.findall(r'\d+\.\s(.*)', suggestions[0])
    return graph_list if graph_list else ["Aucune suggestion extraite."]


def graph_display(client, df):
    st.subheader("Visualisation des Données")
    graphique_selectionne = st.selectbox("Choisissez un type de graphique :", st.session_state.graph_list)

    if st.button("Générer le Graphique"):
        with st.spinner("Génération en cours..."):
            code_plotly = generate_plotly_code(df, graphique_selectionne, client).strip()
            code_plotly = code_plotly.strip('[]')

            # 🔍 Trouver le **dernier** bloc de code entre crochets
            correspondances = re.findall(r"\[(.*?)\]", code_plotly, re.DOTALL)
            correspondances[-1].strip() if correspondances else ""

            with st.expander("Cliquez pour voir le code"):
                st.code(code_plotly, language="python")
        
            if code_plotly:
                try:
                    variables_locales = {"df": df, "go": go, "px": px}
                    exec(code_plotly, globals(), variables_locales)
                    fig = variables_locales.get("fig")

                    if fig:
                        st.plotly_chart(fig)
                        interpretation = interpret_fig(fig, client)
                        st.write(interpretation)
                    else:
                        st.error("❌ Erreur : 'fig' n'a pas été généré.")

                except SyntaxError as e:
                    st.error(f"❌ Erreur de syntaxe dans le code généré : {e}")
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'exécution du code : {e}")
            else:
                st.error("❌ Aucun code valide retourné par Claude.")


def user_graph_display(client, df):
    st.subheader("Suggérer un Graphique :")
    question = st.text_input("Suggestion de Graphique :")

    if st.button("Générer le Graphique Suggéré"):
        with st.spinner("Génération du Graphique Suggéré en cours..."):
            code_plotly2 = generate_plotly_code(df, question, client).strip()
            code_plotly2 = code_plotly2.strip('[]')

            # 🔍 Trouver le **dernier** bloc de code entre crochets
            correspondances2 = re.findall(r"\[(.*?)\]", code_plotly2, re.DOTALL)
            correspondances2[-1].strip() if correspondances2 else ""

            with st.expander("Cliquez pour voir le code"):
                st.code(code_plotly2, language="python")
        
            if code_plotly2:
                try:
                    variables_locales = {"df": df, "go": go, "px": px}
                    exec(code_plotly2, globals(), variables_locales)
                    fig = variables_locales.get("fig")

                    if fig:
                        st.plotly_chart(fig)
                        interpretation = interpret_fig(fig, client)
                        st.write(interpretation)
                    else:
                        st.error("❌ Erreur : 'fig' n'a pas été généré.")

                except SyntaxError as e:
                    st.error(f"❌ Erreur de syntaxe dans le code généré : {e}")
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'exécution du code : {e}")
            else:
                st.error("❌ Aucun code valide retourné par Claude.")


def display_graph_suggestions(df, client):
    """
    Affiche les graphiques suggérés en fonction du jeu de données et permet aux utilisateurs de générer des visualisations.
    """
    if "graph_list" not in st.session_state:
        st.subheader("📌 Graphiques Suggérés")
        suggestions = suggest_graphs(df, client)
        if suggestions:
            st.session_state.graph_list = display_suggestions(suggestions)
        else:
            st.session_state.graph_list = ["Aucune suggestion reçue."]
    else:
        st.subheader("📌 Graphiques Suggérés")
        st.write("\n".join(st.session_state.graph_list))

    # Sélection du graphique
    if "graph_list" in st.session_state:
        graph_display(client, df)

    # Suggestion de graphique par l'utilisateur
    user_graph_display(client, df)
