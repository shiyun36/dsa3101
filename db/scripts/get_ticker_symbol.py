
import yahooquery as yq
from rapidfuzz import process, fuzz
import pandas as pd
import re

def get_ticker_symbol(company_name, company_db_df):
    #clean company name
    company_name = company_name.replace('-', ' ').replace('_', ' ').upper() ## Standardize to upper case

    ## suffix to clean (we try to split the company name and remove the suffix)
    suffixes_to_remove = ['GROUP', 'LIMITED', 'INC', 'CORP', 'CORPORATION', 'PLC']
    suffixes_with_space = ['HEALTHCARE']

    #remove suffix
    for suffix in suffixes_to_remove:
        company_name = re.sub(r'(?i)'+ re.escape(suffix), '', company_name) 
    
    # for healthcare, if no space then add space otherwise leave
    for suffix in suffixes_with_space:
        company_name = re.sub(r'(?<=\w)' + re.escape(suffix) + r'\b', ' ' + suffix, company_name)

    ## yq search first
    data = yq.search(company_name)
    if data['quotes'] != []: #if not empty
        data_list = data['quotes']
        data_list_shortnames = [x['shortname'].upper() if 'shortname' in x else '' for x in data_list]
        data_list_names = [x['longname'].upper() for x in data_list] ##UPPER CASE to COMPARE
        matches_long = process.extract(company_name, data_list_names, limit=1)
        matches_short = process.extract(company_name, data_list_shortnames, limit=1)
        if matches_long[0][1] > 60 or matches_short[0][1] > 60:
            # Choose the best match from either list (longname or shortname)
            if matches_long[0][1] > matches_short[0][1]:
                symbol = data['quotes'][matches_long[0][2]]['symbol']
            else:
                symbol = data['quotes'][matches_short[0][2]]['symbol']
            
            return symbol
    #else we do fuzzy matching in our db as yq can only search accurate names
    matches = process.extract(company_name, company_db_df['company_name'])
    if matches[0][1] > 70:
        index_ticker = matches[0][2]
        ticker = company_db_df.iloc[index_ticker]['symbol']
        return ticker
    #else
    return None