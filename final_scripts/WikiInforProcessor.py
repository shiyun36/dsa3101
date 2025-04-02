import os
import pandas as pd
from final_scripts.GeneralCompanyInfoProcessor import GeneralCompanyInfoProcessor
from final_scripts.Supabase_Query import SupabaseESGData

class CompanyInfoUpdater:
    def __init__(self, saved_url_df: pd.DataFrame):
        """
        Initializes the updater with the path to the CSV file and a DataFrame containing saved URLs.

        Parameters:
          csv_path (str): Path to the CSV file that stores processed company-year data.
          saved_url_df (pd.DataFrame): DataFrame containing saved URLs.
        """
        self.csv_path = './files/wiki/wiki_final.csv'
        self.saved_url_df = saved_url_df

    def _read_existing_tuples(self) -> set:
        """
        Reads the local CSV file and extracts a set of (Company, Year) tuples.
        Returns an empty set if the file does not exist or the columns are missing.
        """
        if os.path.exists(self.csv_path):
            df_existing = pd.read_csv(self.csv_path)
            if 'Company' in df_existing.columns and 'Year' in df_existing.columns:
                return list(zip(df_existing['Company'], df_existing['Year']))
        return []

    def _extract_input_tuples(self, input_df: pd.DataFrame) -> set:
        """
        Extracts a set of (Company, Year) tuples from the provided DataFrame.
        Assumes the DataFrame contains 'Company' and 'Year' columns.
        """
        #new_df = input_df[['Company', 'Year']].drop_duplicates()
        #return list(zip(new_df['Company'], new_df['Year']))
        subset = input_df[['company', 'year']]
        unique_pairs = subset.drop_duplicates()
        unique_pairs['year'] = unique_pairs['year'].astype(int)
        company_year_tuples = list(unique_pairs.itertuples(index=False, name=None))
        return company_year_tuples
    
    def find_missing_tuples(self, input_tuples: list, existing_tuples: list) -> list:
        """
          input_tuples but not in existing_tuples.
        """
        input_set = set(input_tuples)
        existing_set = set(existing_tuples)
        missing_set = input_set - existing_set
        return list(missing_set)
    
    def find_industry_country(self, input_df: pd.DataFrame, company: str, year: any) -> tuple:
        """
        : (industry, country) if a matching row is found; otherwise (None, None).
        """
        # Filter the DataFrame for rows matching the given company and year.
        matching_rows = input_df[(input_df['company'] == company) & (input_df['year'].astype(str) == str(year))]
        print("input_df: " + str(input_df))
        print("in fn company:"+ str(company))
        print("in fn year:"+ str(year))
        print(matching_rows)
    
        if not matching_rows.empty:
            # Take the first matching row.
            row = matching_rows.iloc[0]
            industry = row.get('industry', None)
            country = row.get('country', None)
            return industry, country
        else:
            return None, None

    def update_from_df(self, input_df: pd.DataFrame):
        """   
         update the original CSV file with newly processed rows.
        """
        # Read processed tuples from the CSV file.
        existing_tuples = self._read_existing_tuples()
        # Extract tuples from the input DataFrame.
        input_tuples = self._extract_input_tuples(input_df)
        # Find tuples that are missing in the CSV.
        tuples_to_process = self.find_missing_tuples(input_tuples, existing_tuples)

        print("Process (Company, Year) tuples:", tuples_to_process)

        # Process each missing company-year tuple.
        for company, year in tuples_to_process:
            print(f"Processing missing tuple: ({company}, {year})")
            industry, country = self.find_industry_country(self.saved_url_df, company, year)

            processor = GeneralCompanyInfoProcessor(
                year=year,
                company=company,
                country=country,
                industry=industry,
                output_csv=self.csv_path,
                saved_url_file=self.saved_url_df
            )
            # This method is assumed to query OpenAI, produce results, and append them to the CSV.
            processor.ask_openai_from_file()

    def form_supabase_input(self, input_df) -> pd.DataFrame:
        """
        returned DataFrame contains the rows that need to be inserted into Supabase.
        """
        self.update_from_df(input_df)
        print("im done here at csv")

        # Step 2: Get (Company, Year) tuples from Supabase.
        supabase_instance = SupabaseESGData(table_name='general_company_info_table')
        supabase_tuples = supabase_instance.get_company_year_tuples()  # Returns a list of tuples.
        supabase_set = set(supabase_tuples)
        print("Supabase tuples:", supabase_set)

        if os.path.exists(self.csv_path):
            local_df = pd.read_csv(self.csv_path)
            if 'Company' in local_df.columns and 'Year' in local_df.columns:
                local_tuples = set(zip(local_df['Company'], local_df['Year']))
            else:
                print("CSV does not contain 'Company' and 'Year' columns.")
                return pd.DataFrame()
        else:
            print("CSV file does not exist.")
            return pd.DataFrame()

        str_local_tuples = {(company, str(year)) for company, year in local_tuples}

        missing_in_supabase = str_local_tuples - supabase_set
        print("Tuples missing in Supabase:", missing_in_supabase)
        missing_in_supabase_destringified = {(company, int(year)) for company, year in missing_in_supabase}
        missing_rows_df = local_df[local_df.apply(lambda row: (row['Company'], row['Year']) in missing_in_supabase_destringified, axis=1)]
        
        return missing_rows_df
        
    

if __name__ == "__main__":
    saved_url_df = pd.read_csv('./files/wiki/wiki_final.csv')
    updater = CompanyInfoUpdater(saved_url_df=saved_url_df)
    
    # Example input DataFrame with new company-year pairs.
    input_df = pd.DataFrame({
        "Company": ["PUMAENERGY", "MORGAN STANLEY", "EXAMPLECO"],
        "Year": [2024, 2023, 2024]
    })
    
    # Update the CSV file by processing missing company-year tuples.
    updater.update_from_df(input_df)