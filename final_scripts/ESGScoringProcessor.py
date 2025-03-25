import pandas as pd
import numpy as np
import logging

class ESGScoringProcessor:
    def __init__(self, df):
        '''
        Input: ESG scoring dataframe
        Purpose: converts the ESG scoring dataframe generated from rag.py into a format suitable for esg_rag_table db
        '''
        self.df = df
        self.num_metrics = self.calculate_num_metrics()

    def calculate_num_metrics(self):
        """
        Calculates the number of metrics in the dataframe.
        """
        return int((self.df.shape[1] - 4) / 2)

    def extract_company_info(self):
        """
        Extracts company-related information (Company, Year, Industry, Country).
        """
        return self.df.iloc[:, 0:4]

    def get_extracted_values(self):
        """
        Extracts the values of each ESG metric from the dataframe.
        """
        num_metrics = self.num_metrics
        df_extracted_values = self.df.iloc[:, 0: 4 + num_metrics]
        df_extracted_values.drop(columns=["Company", "Year", "Industry", "Country"], errors="ignore", inplace=True)
        return df_extracted_values

    def extract_scoring_data(self):
        """
        Extracts the scoring data (final score) for each ESG metric.
        """
        df_company_info = self.extract_company_info()
        df_scoring = self.df.iloc[:, -self.num_metrics:]
        return pd.concat([df_company_info, df_scoring], axis=1)

    def clean_scoring_data(self, df_scoring):
        """
        Cleans the scoring data, replacing 'N/A' values with NaN.
        """
        df_scoring.replace("N/A", pd.NA, inplace=True)
        return df_scoring

    def reshape_to_esg_rag_schema(self, df_scoring):
        """
        Reshapes the scoring dataframe to match the 'esg_rag' schema.
        """
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
        return reshaped_df

    def combine_extracted_values(self, df_extracted_values, reshaped_df):
        """
        Combine extracted values with the reshaped dataframe.
        """
        extracted_values = []
        for col in df_extracted_values.columns:
            extracted_values.extend(df_extracted_values[col].tolist())
        reshaped_df["extracted_values"] = extracted_values[:len(reshaped_df)]
        return reshaped_df

    def reorder_columns(self, df):
        """
        Reorders the columns to match the desired output format.
        """
        return df[["company", "year", "industry", "country", "topic", "extracted_values", "final_score"]]

    def convert_to_esg_rag_dataframe(self):
        """
        Main method to convert the ESG scoring dataframe into a format suitable for the 'esg_rag' table.
        """
        try:
            df_extracted_values = self.get_extracted_values()
            df_scoring = self.extract_scoring_data()
            df_scoring = self.clean_scoring_data(df_scoring)
            reshaped_df = self.reshape_to_esg_rag_schema(df_scoring)
            final_df = self.combine_extracted_values(df_extracted_values, reshaped_df)
            final_df = self.reorder_columns(final_df)
        
            return final_df
        except Exception as e:
            logging.error(f"Error in converting ESG scoring dataframe: {e}")
            return pd.DataFrame(columns=["company", "year", "industry", "country", "topic", "extracted_values", "final_score"])

# Example usage:
# def main(df):
#     processor = ESGScoringProcessor(df)
#     result_df = processor.convert_to_esg_rag_dataframe()
#     return result_df

# Example usage
# df = pd.read_csv("path_to_file.csv")  # Replace with actual dataframe
# esg_rag_df = main(df)
# print(esg_rag_df)
