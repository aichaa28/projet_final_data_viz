import pytest
import pandas as pd
import sys
import os
from projet_final_data_viz.tapas_code import (
    load_tapas_model, validate_question, process_aggregation,
    detect_question_type
)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


def test_load_tapas_model():
    tokenizer, model = load_tapas_model()
    assert tokenizer is not None, "Le tokenizer ne doit pas être None."
    assert model is not None, "Le modèle ne doit pas être None."


def test_validate_question():
    assert validate_question("Quel est le total des ventes ?") is True
    assert validate_question("   ") is False
    assert validate_question("") is False


def test_process_aggregation():
    df = pd.DataFrame({
        'Category': ['A', 'A', 'B', 'B'],
        'Sales': [100, 200, 150, 250]
    })
    
    assert process_aggregation(df, 'sum', 'Sales') == "700"
    assert process_aggregation(df, 'mean', 'Sales') == "175.00"
    assert process_aggregation(df, 'count', 'Sales') == "4"
    assert process_aggregation(df, 'min', 'Sales') == "100"
    assert process_aggregation(df, 'max', 'Sales') == "250"


def test_detect_question_type():
    df = pd.DataFrame({
        'Category': ['A', 'B', 'C'],
        'Sales': [100, 200, 300]
    })
    
    assert detect_question_type("What is the sum of Sales?", df) == ('aggregation', {'operation': 'sum', 'column': 'Sales'})
    assert detect_question_type("Show all Categories", df) == ('default', None)  # Expecting 'default', None


if __name__ == "__main__":
    pytest.main()