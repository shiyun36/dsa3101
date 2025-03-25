import pandas as pd
import json

dir_json = "../files/sg_finance_score.json"
dir_csv = "../files/sg_finance_score.csv"

def convert_json_to_esg_rag_dataframe(json_path, csv_path):
    '''
    Input: 
    1. json file containing company ESG scores
    2. csv file containing extracted ESG related text data 
    Output: df combining company, year, extracted values and scores of the Governance, Environmental and Social categories respectively. 
    Purpose: Combines ESG scores stored in the JSON file with extracted ESG values from the csv file, and structure it to fit the ESG RAG database format. 
    '''
    
    # Load json data
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Load csv data
    df_csv = pd.read_csv(csv_path)
    df_csv.drop(columns=["Company", "Year"], errors = "ignore", inplace = True)

    extracted_values = []
    for col in df_csv.columns:
        extracted_values.extend(df_csv[col].tolist())

    # Converting jon to a DataFrame
    records = []
    for bank, years in data.items():
        for year, indicators in years.items():
            record = {'Bank': bank, 'Year': year}
            record.update(indicators)
            records.append(record)

    df_json = pd.DataFrame(records)

    # Clean up and format columns
    df_json.replace("N/A", pd.NA, inplace = True)
    df_json['Year'] = df_json['Year'].astype(float).astype(int)

    # Reshape json DataFrame to match esg_rag schema
    reshaped_df = df_json.melt(
        id_vars=["Bank", "Year"],
        var_name="topic",
        value_name="final_score"
    )

    reshaped_df.rename(columns={
        "Bank": "company",
        "Year": "year"
    }, inplace=True)

    # Combine CSV values as 'extracted_values'
    reshaped_df["extracted_values"] = extracted_values[:len(reshaped_df)]

    # Reorder columns
    reshaped_df = reshaped_df[["company", "year", "topic", "extracted_values", "final_score"]]

    return reshaped_df