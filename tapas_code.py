import re
import pandas as pd
import streamlit as st
from transformers import TapasTokenizer, TapasForQuestionAnswering
from collections import OrderedDict


@st.cache_resource
def load_tapas_model():
    """Load and cache the TAPAS tokenizer and model."""
    try:
        tokenizer = TapasTokenizer.from_pretrained(
            'google/tapas-base-finetuned-wtq'
        )
        model = TapasForQuestionAnswering.from_pretrained(
            'google/tapas-base-finetuned-wtq'
        )
        return tokenizer, model
    except Exception as e:
        st.error(f"Error loading TAPAS model: {e}")
        return None, None


def get_cell_value(df, coord):
    """Get the cell value from the DataFrame given the coordinates."""
    try:
        row_idx, col_idx = coord
        if 0 <= row_idx < df.shape[0] and 0 <= col_idx < df.shape[1]:
            value = df.iloc[row_idx, col_idx]
            return str(value) if pd.notnull(value) else ""
        return ""
    except Exception:
        return ""


def split_dataframe(df, max_rows=50):
    """Split the DataFrame into chunks of a specified maximum size."""
    try:
        if len(df) <= max_rows:
            return [df]
        chunks = [df.iloc[i:i + max_rows].copy() for i in range(0, len(df), max_rows)]
        return chunks
    except Exception as e:
        st.error(f"Error splitting DataFrame: {e}")
        return [df]


def validate_question(question):
    """Validate if the question is non-empty."""
    if not question or not question.strip():
        st.warning("Please enter a valid question.")
        return False
    return True


def process_aggregation(df, operation, column, group_by=None):
    """Handle both simple and grouped aggregation operations."""
    try:
        if group_by:
            if operation == 'sum':
                result = df.groupby(group_by)[column].sum()
            elif operation in ['mean', 'average']:
                result = df.groupby(group_by)[column].mean()
            elif operation == 'count':
                result = df.groupby(group_by)[column].count()
            elif operation == 'min':
                result = df.groupby(group_by)[column].min()
            elif operation == 'max':
                result = df.groupby(group_by)[column].max()

            # Format grouped results
            formatted_results = []
            for group, value in result.items():
                if 'price' in column.lower() or 'amount' in column.lower():
                    formatted_value = f"${value:,.2f}"
                else:
                    formatted_value = f"{value:.2f}"
                formatted_results.append(f"{group}: {formatted_value}")
            return "\n".join(formatted_results)
        else:
            if operation == 'sum':
                result = df[column].sum()
                return f"${result:,.2f}" if 'amount' in column.lower() or 'price' in column.lower() else f"{result:,.0f}"
            elif operation in ['mean', 'average']:
                result = df[column].mean()
                return f"{result:.2f}"
            elif operation == 'count':
                return str(len(df))
            elif operation == 'min':
                return str(df[column].min())
            elif operation == 'max':
                return str(df[column].max())
    except Exception as e:
        return f"Error in aggregation: {str(e)}"


def detect_question_type(question, df):
    """Detect the type of question based on keywords and patterns."""
    question_lower = question.lower()

    # Check for grouped aggregation pattern
    group_agg_pattern = r'(average|mean|sum|count|min|max) of (\w+) by (\w+)'
    group_match = re.search(group_agg_pattern, question_lower)
    if group_match:
        operation, measure_col, group_col = group_match.groups()
        # Match column names more flexibly
        measure_col = next((col for col in df.columns if col.lower().replace('_', '') in measure_col.replace('_', '')), None)
        group_col = next((col for col in df.columns if col.lower().replace('_', '') in group_col.replace('_', '')), None)
        if measure_col and group_col:
            return 'group_aggregation', {
                'operation': operation,
                'column': measure_col,
                'group_by': group_col
            }

    # Regular aggregation patterns
    agg_patterns = {
        'sum': r'sum of|total|sum',
        'mean': r'average|mean|avg',
        'count': r'count|how many|number of',
        'min': r'minimum|min|lowest',
        'max': r'maximum|max|highest'
    }

    # Check for regular aggregation
    for operation, pattern in agg_patterns.items():
        if re.search(pattern, question_lower):
            for col in df.columns:
                if col.lower() in question_lower:
                    return 'aggregation', {'operation': operation, 'column': col}

    # Check for column listing
    list_keywords = ['show', 'list', 'what are', 'display', 'give me', 'what is in']
    for col in df.columns:
        if col.lower() in question_lower and any(kw in question_lower for kw in list_keywords):
            return 'column', col

    return 'default', None


def format_answers(answers, max_display=50):
    """Format the answers for display."""
    if not answers:
        return "No answers found."

    if isinstance(answers, (int, float, str)):
        return str(answers)

    unique_answers = list(OrderedDict.fromkeys(answers))

    if len(unique_answers) > max_display:
        return {
            'type': 'paginated',
            'answers': unique_answers,
            'total': len(unique_answers)
        }
    else:
        formatted = "\n".join(f"• {answer}" for answer in unique_answers)
        return {
            'type': 'direct',
            'content': formatted,
            'total': len(unique_answers)
        }


def process_question(question, df, max_rows=50):
    """Process the question and return the answer."""
    if not validate_question(question):
        return None
    tokenizer, model = load_tapas_model()
    df = df.fillna('')
    question_type, info = detect_question_type(question, df)

    # Handle group aggregation
    if question_type == 'group_aggregation':
        return process_aggregation(df, info['operation'], info['column'], info['group_by'])

    # Handle regular aggregation
    if question_type == 'aggregation':
        return process_aggregation(df, info['operation'], info['column'])

    # Handle column listing
    if question_type == 'column' and info in df.columns:
        unique_values = df[info].dropna().unique().tolist()
        return format_answers(unique_values)

    # Default TAPAS processing for other questions
    df_chunks = split_dataframe(df, max_rows)
    all_answers = []

    for chunk in df_chunks:
        try:
            chunk_str = chunk.astype(str)
            inputs = tokenizer(
                table=chunk_str,
                queries=[question],
                padding='max_length',
                return_tensors="pt",
                truncation=True
            )

            outputs = model(**inputs)
            predicted_answer_coords, predicted_agg_indices = tokenizer.convert_logits_to_predictions(
                inputs,
                outputs.logits.detach(),
                outputs.logits_aggregation.detach()
            )

            if predicted_answer_coords[0]:
                cell_values = [get_cell_value(chunk_str, coord) for coord in predicted_answer_coords[0]]
                clean_values = [val.strip() for val in cell_values if val.strip()]
                all_answers.extend(clean_values)

        except Exception:
            continue

    if not all_answers:
        return "Could not find an answer in the table."

    return format_answers(all_answers)


def show_tapas_ui(df):
    """Display the TAPAS UI for the given DataFrame."""
    st.write("Available columns:", ", ".join(df.columns))
    st.write("Table preview:")
    st.dataframe(df)

    question = st.text_input("Enter your question:")
    if st.button("Get Answer"):
        with st.spinner("Processing your question..."):
            answer = process_question(question, df)

            if isinstance(answer, dict):
                if answer['type'] == 'paginated':
                    st.write(f"Found {answer['total']} unique answers")
                    items_per_page = 20
                    num_pages = (answer['total'] + items_per_page - 1) // items_per_page
                    if num_pages > 1:
                        page = st.selectbox('Select page:', range(1, num_pages + 1))
                        start_idx = (page - 1) * items_per_page
                        end_idx = min(start_idx + items_per_page, answer['total'])
                        current_items = answer['answers'][start_idx:end_idx]
                        for item in current_items:
                            st.write(f"• {item}")
                        st.write(f"Showing {start_idx + 1}-{end_idx} of {answer['total']} items")
                    else:
                        for item in answer['answers']:
                            st.write(f"• {item}")
                else:
                    st.write(f"Found {answer['total']} unique answers:")
                    st.write(answer['content'])
            else:
                st.write("🧠 Answer:", answer)