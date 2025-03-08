import tabula
import pandas as pd


def extract_tables(pdf):
    data = tabula.read_pdf(pdf, pages='all')
    dfs_json = []
    for i in data:
        if i.isna().mean().mean() <= 0.45 and i.shape[0] > 1:
            dfs_json.append(i.to_json())
    return dfs_json