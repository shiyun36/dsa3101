import pandas as pd
import numpy as np

class ESGRAGDataframeConverter:
    def __init__(self, csv_path):
        """
        Initialize the converter by loading the CSV file.
        """
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)

    def convert(self):
        """
        Converts the scoring metric CSV into an ESG RAG DataFrame.
        Extracts shared metadata from the last row and transforms metric columns into rows.
        """
        # Extract shared metadata from the last row
        company = self.df.iloc[-1]["Company"]
        year = self.df.iloc[-1]["Year"]
        industry = self.df.iloc[-1]["Industry"]
        country = self.df.iloc[-1]["Country"]

        records = []

        # Loop through each column to find metric and its score
        for col in self.df.columns:
            if col.endswith('_numScore'):
                topic = col.replace('_numScore', '')
                extracted_values = self.df.iloc[-1][topic]
                final_score = self.df.iloc[-1][col]

                records.append({
                    'company': company,
                    'year': year,
                    'industry': industry,
                    'country': country,
                    'topic': topic,
                    'extracted_values': extracted_values,
                    'final_score': final_score
                })

        final_df = pd.DataFrame(records)
        return final_df