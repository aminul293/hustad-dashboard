
import pandas as pd

def load_data(file_path):
    return pd.read_csv(file_path)

def format_currency(amount):
    return "${:,.2f}".format(amount)
