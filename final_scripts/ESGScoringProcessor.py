import pandas as pd
import numpy as np

class ESGRAGDataframeConverter:
    def __init__(self, csv_path, num_companies):
        """
        Initialize the converter by loading the CSV file.
        """
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        self.num_companies = num_companies

    def convert(self):
        """
        Converts the scoring metric CSV into an ESG RAG DataFrame.
        Extracts shared metadata from the last row and transforms metric columns into rows.
        """

        # Loop through each column to find metric and its score
        df = self.df.tail(self.num_companies)

        # Prepare a list to store transformed records
        records = []

        # Loop through each row
        for _, row in df.iterrows():
            company = row["Company"]
            year = row["Year"]
            industry = row["Industry"]
            country = row["Country"]

            # Loop through each column to find metric and its score
            for col in df.columns:
                if col.endswith('_numScore'):
                    topic = col.replace('_numScore', '')
                    extracted_values = row.get(topic, pd.NA)
                    final_score = row[col]
                    
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
