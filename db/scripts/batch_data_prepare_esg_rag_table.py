from tqdm import tqdm
import json
import pandas as pd

def batch_data_prepare_esg_rag_table(df, batch_size):
    batch_data = [] #batch of data to append
    batches = [] #index of batches

    #batch data_preparation
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Prepare batches", unit="document", leave=True, ncols=100):
        batch_data.append((
            row['company'],
            row['industry'],
            row['country'],
            int(row['year']),
            row['topic'],
            row["extracted_values"],
            None if pd.isna(row["final_score"]) else float(row["final_score"]),
        )) #appends a row to batch_data in tuple format for batch format

        if len(batch_data) >= batch_size: #eg 100-200?
            batches.append(batch_data)
            batch_data = [] #reset batch
    
    # Append leftovers as above code doesnt account for it
    batches.append(batch_data)
    return batches