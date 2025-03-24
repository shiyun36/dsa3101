
import yahooquery as yq
from rapidfuzz import process, fuzz
import pandas as pd

def get_ticker_symbol(company_name, company_db_df):
    #clean company name
    company_name = company_name.replace('-', ' ')
    company_name = company_name.replace('_', ' ')
    ## yq search first
    data = yq.search(company_name)
    if data['quotes'] != []:
        symbol = data['quotes'][0]['symbol'] ##get first result
        return symbol
    #else we do fuzzy matching in our db as yq can only search accurate names
    matches = process.extract(company_name, company_db_df['company_name'])
    if matches[0][1] > 75:
        index_ticker = matches[0][2]
        ticker = company_db_df.iloc[index_ticker]['symbol']
        return ticker
    return None