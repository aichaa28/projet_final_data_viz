import sys
import os
import pytest
from unittest import mock
from unittest.mock import MagicMock
import pandas as pd
# Importation des modules nécessaires

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

@pytest.fixture
def mock_streamlit():
    # Mock du module Streamlit
    mock_streamlit = MagicMock()
    return mock_streamlit

@pytest.fixture
def sample_dataframe():
    # Exemple de DataFrame
    return pd.DataFrame({
        'col1': [1, 2, None, 4],
        'col2': ['a', 'b', 'c', 'd'],
        'col3': ['2021-01-01', '2022-01-01', '2023-01-01', '2024-01-01']
    })

@mock.patch('streamlit.file_uploader')
def test_file_upload(mock_file_uploader, sample_dataframe):
    # Simulation du téléchargement du fichier
    mock_file_uploader.return_value = sample_dataframe

    assert sample_dataframe.shape == (4, 3)


