import pandas as pd
import numpy as np
import logging

class RagScoreProcessor:
    def __init__(self, csv_file):
        '''
        Input: Path to ESG scoring CSV file.
        Purpose: Converts the last row of the CSV (from RAG output) into a format suitable for the 'esg_rag_table' schema.
        '''
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file)

    def convert_to_esg_rag_dataframe(self):
        """
        Converts only the last row of the dataframe into the esg_rag format.
        """
        try:
            last_row = self.df.iloc[-1]

            # Extract metadata
            company = last_row["Company"]
            year = last_row["Year"]
            industry = last_row["Industry"]
            country = last_row["Country"]

            records = []

            for col in self.df.columns:
                if col.endswith('_numScore'):
                    topic = col.replace('_numScore', '')
                    extracted_value = last_row.get(topic, pd.NA)
                    final_score = last_row[col]

                    records.append({
                        'company': company,
                        'year': year,
                        'industry': industry,
                        'country': country,
                        'topic': topic,
                        'extracted_values': extracted_value,
                        'final_score': final_score
                    })

            return pd.DataFrame(records)

        except Exception as e:
            logging.error(f"Error in convert_to_esg_rag_dataframe: {e}")
            return pd.DataFrame(columns=["company", "year", "industry", "country", "topic", "extracted_values", "final_score"])
