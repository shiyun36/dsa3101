import pandas as pd
import numpy as np 
 
def convert_scoring_metric_to_esg_rag_dataframe(csv_path):
    '''
    Input: ESG scoring dataframe
    Purpose: converts the ESG scoring dataframe generated from rag.py into a format suitable for esg_rag_table db
    '''
    df = pd.read_csv(csv_path)
    df = df.tail(1)

    # Obtain the number of Metrics 
    num_metrics = int((len(df.columns) - 4)/2)

    # Forms a dataframe of the company info + extracted values of each esg metric from the llm
    df_extracted_values = df.iloc[:, 0 : 4 + num_metrics]

    # Forms a dataframe of the company info + final score of each esg metric from the llm
    df_company_info = df.iloc[:, 0:4]
    df_scoring = df.iloc[:,-num_metrics:]
    df_scoring = pd.concat([df_company_info, df_scoring], axis = 1)

    # Load csv data
    df_extracted_values.drop(columns=["Company", "Year", "Industry", "Country"], errors = "ignore", inplace = True)

    extracted_values = []
    for col in df_extracted_values.columns:
        extracted_values.extend(df_extracted_values[col].tolist())

    # Clean up and format columns
    df_scoring.replace("N/A", pd.NA, inplace = True)

    # Reshape esg_score dataframe to match esg_rag schema
    reshaped_df = df_scoring.melt(
        id_vars=["Company", "Year", "Industry", "Country"],
        var_name="topic",
        value_name="final_score"
    )

    reshaped_df.rename(columns={
        "Company": "company",
        "Year": "year",
        "Industry": "industry",
        "Country": "country"
    }, inplace=True)

    # Combine CSV values as 'extracted_values'
    reshaped_df["extracted_values"] = extracted_values[:len(reshaped_df)]

    # Reorder columns
    reshaped_df = reshaped_df[["company", "year", "industry", "country", "topic", "extracted_values", "final_score"]]

    return reshaped_df