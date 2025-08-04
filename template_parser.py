# template_parser.py
import pandas as pd

def parse_template(file):
    """
    Parses the AM template Excel file into a DataFrame.
    Assumes the first row is headers, first column is time slots.
    """
    df = pd.read_excel(file, engine="openpyxl")
    df = df.fillna("")
    return df
