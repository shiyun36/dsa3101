import pandas as pd
import numpy as np

def convert_scoring_metric_to_esg_rag_dataframe(csv_path):
    # Load your CSV file
    df = pd.read_csv(csv_path)

    # Extract shared metadata from the last row
    company = df.iloc[-1]["Company"]
    year = df.iloc[-1]["Year"]
    industry = df.iloc[-1]["Industry"]
    country = df.iloc[-1]["Country"]

    # Prepare a list to store transformed records
    records = []

    # Loop through each column to find metric and its score
    for col in df.columns:
        if col.endswith('_numScore'):
            topic = col.replace('_numScore', '')
            extracted_values = df.iloc[-1][topic]
            final_score = df.iloc[-1][col]
            
            records.append({
                'company': company,
                'year': year,
                'industry': industry,
                'country': country,
                'topic': topic,
                'extracted_values': extracted_values,
                'final_score': final_score
            })

    # Create the final DataFrame
    final_df = pd.DataFrame(records)
    return final_df

        
