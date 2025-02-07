# tests/test_app.py
import sys
import os
import pytest
import pandas as pd
from unittest import mock
from unittest.mock import MagicMock
from projet_final_data_viz.description import describe_dataset 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))




@pytest.fixture
def mock_streamlit():
    # Mock the Streamlit module
    mock_streamlit = MagicMock()
    return mock_streamlit

@pytest.fixture
def sample_dataframe():
    # Create a sample dataframe
    return pd.DataFrame({
        'col1': [1, 2, None, 4],
        'col2': ['a', 'b', 'c', 'd'],
        'col3': ['2021-01-01', '2022-01-01', '2023-01-01', '2024-01-01']
    })


@mock.patch('streamlit.file_uploader')
def test_file_upload(mock_file_uploader, sample_dataframe):
    # Mock the uploaded file process
    mock_file_uploader.return_value = sample_dataframe

    assert sample_dataframe.shape == (4, 3)
        
        
@mock.patch('streamlit.file_uploader')
def test_tabs_functionality(mock_streamlit, sample_dataframe):
    # Simule ce que tabs() retourne
    tab1, tab2, tab3 = mock.Mock(), mock.Mock(), mock.Mock()
    mock_streamlit.tabs.return_value = [tab1, tab2, tab3]

    # Simule les méthodes __enter__ et __exit__ pour chaque onglet
    tab1.__enter__ = mock.Mock()
    tab2.__enter__ = mock.Mock()
    tab3.__enter__ = mock.Mock()
    tab1.__exit__ = mock.Mock()
    tab2.__exit__ = mock.Mock()
    tab3.__exit__ = mock.Mock()

    # Mock the tab buttons and Streamlit session states
    tab1, tab2, tab3 = mock_streamlit.tabs([
        "Dataset Description", "TAPAS Analysis", "Claude Analysis"
    ])

    with tab1:
        describe_dataset(sample_dataframe)
        mock_streamlit.dataframe.assert_any_call(sample_dataframe.head(), use_container_width=True)

    with tab2:
        mock_streamlit.text_input.return_value = "What is the sum of col1?"
        # Mock TAPAS processing function if needed
        mock_streamlit.spinner.return_value = "Processing..."
        mock_streamlit.write.assert_any_call("🤖 TAPAS Answer:", "sum")

    with tab3:
        mock_streamlit.text_input.return_value = "What are the trends?"
        mock_streamlit.write.assert_any_call("🧠 Claude Answer:", "trends")
