from tqdm import tqdm

def batch_data_prepare_esg_text(df):
    batch_data = [] #batch of data to append
    batches = [] #index of batches
    
    #batch data_preparation
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Prepare batches", unit="document", leave=True, ncols=100):
        batch_data.append((
            row['company'],
            int(row['year']),
            row['country'],
            row['industry'],
            row['esg_text'],
        )) #appends a row to batch_data in tuple format for batch format

        if len(batch_data) >= 200: #eg 100-200?
            batches.append(batch_data)
            batch_data = [] #reset batch
    
    # Append leftovers as above code doesnt account for it
    batches.append(batch_data)
    return batches