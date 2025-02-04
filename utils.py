import pandas as pd

def load_data(file):
    """Charge un fichier CSV en DataFrame Pandas."""
    return pd.read_csv(file)

def get_columns_summary(df):
    """Retourne un résumé des colonnes du dataset."""
    return df.dtypes.to_dict()
