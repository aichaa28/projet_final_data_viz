# tests/test_description.py
import sys
import os
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from projet_final_data_viz.description import describe_dataset
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture
def sample_dataframe():
    """ Crée un DataFrame de test """
    data = {
        'col1': [1, 2, np.nan, 4],  # Numérique avec une valeur NaN
        'col2': ['a', 'b', 'c', 'd'],  # Catégorique
        'col3': pd.to_datetime(['2021-01-01', '2022-01-01', '2023-01-01', '2024-01-01'])  # Date
    }
    return pd.DataFrame(data)


@patch("streamlit.subheader")
@patch("streamlit.write")
@patch("streamlit.metric")
@patch("streamlit.dataframe")
def test_describe_dataset(mock_dataframe, mock_metric, mock_write, mock_subheader, sample_dataframe):
    """ Teste la fonction describe_dataset avec un DataFrame de test """
    describe_dataset(sample_dataframe)

    # Vérifier les appels des composants Streamlit
    mock_subheader.assert_called_with("Aperçu du Jeu de Données")

    mock_write.assert_any_call("**Informations de base :**")
    mock_metric.assert_any_call("Lignes", 4)
    mock_metric.assert_any_call("Colonnes", 3)
    mock_metric.assert_any_call("Valeurs Manquantes", 1)
    mock_metric.assert_any_call("Doublons", 0)
    mock_metric.assert_any_call("Colonnes Numériques", 1)
    mock_metric.assert_any_call("Colonnes Catégorielles", 1)
    mock_metric.assert_any_call("Colonnes de Date", 1)
    mock_metric.assert_any_call("Mémoire (MB)", "0.00")

    mock_dataframe.assert_called()

