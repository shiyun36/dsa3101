import pandas as pd
import json

dir = "../files/sg_finance_score.json"

def convert_json_to_esg_rag_dataframe(dir):
    with open(dir, 'r') as f:
        data = json.load(f)

    records = []
    for bank, years in data.items():
        for year, indicators in years.items():
            record = {'Bank': bank, 'Year': year}
            record.update(indicators)
            records.append(record)

    df = pd.DataFrame(records)

    # Clean up and format columns
    df.replace("N/A", pd.NA, inplace=True)
    df['Year'] = df['Year'].astype(float).astype(int)

    # Reshape to match esg_rag schema
    reshaped_df = df.melt(
        id_vars=["Bank", "Year"],
        var_name="topic",
        value_name="final_score"
    )

    reshaped_df.rename(columns={
        "Bank": "company",
        "Year": "year"
    }, inplace=True)

    # Create JSON-like column for extracted_values
    reshaped_df["extracted_values"] = reshaped_df.apply(
        lambda row: {row["topic"]: row["final_score"]}, axis=1
    )

    reshaped_df = reshaped_df[["company", "year", "topic", "extracted_values", "final_score"]]

    return reshaped_df
