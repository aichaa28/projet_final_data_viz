# tests/test_app.py
import streamlit as st
from unittest import mock
import sys
import os
from projet_final_data_viz.auth import auth_page 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))


# Mocking the TAPAS model loading
@mock.patch('transformers.TapasForQuestionAnswering.from_pretrained')
@mock.patch('transformers.TapasTokenizer.from_pretrained')
@mock.patch('streamlit.text_input')
@mock.patch('streamlit.button')
@mock.patch('streamlit.rerun')
def test_auth_page(mock_rerun, mock_button, mock_text_input, mock_tapas_tokenizer, mock_tapas_model):
    # Mocking the user input
    mock_text_input.return_value = "fake_api_key"  # Simulate entering the API key
    mock_button.return_value = True  # Simulate clicking the submit button
    
    # Mocking the TAPAS model loading to avoid downloading the real model during the test
    mock_tapas_tokenizer.return_value = "mocked_tokenizer"
    mock_tapas_model.return_value = "mocked_model"
    
    # Run the authentication page function
    auth_page()

    # Check if the correct functions were called
    mock_text_input.assert_called_once_with("Entrez votre clé API Claude :", type="password")
    mock_button.assert_called_once_with("Soumettre")
    mock_tapas_tokenizer.assert_called_once_with('google/tapas-base-finetuned-wtq')
    mock_tapas_model.assert_called_once_with('google/tapas-base-finetuned-wtq')
    mock_rerun.assert_called_once()

    # Check if Streamlit's session state is updated as expected
    assert st.session_state['authentication_status'] is True
    assert 'tapas_tokenizer' in st.session_state
    assert 'tapas_model' in st.session_state
    assert 'claude_api_key' in st.session_state
    assert st.session_state['claude_api_key'] == "fake_api_key"

