import os
from supabase import create_client, Client

class SupabaseESGData:
    """
    A class to connect to Supabase and retrieve ESG data.
    """
    def __init__(self, table_name: str):
        """
        Initializes the Supabase client and sets the table name.
        
        Expects the environment variables 'SUPABASE_URL' and 'SUPABASE_KEY' to be set.
        """
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.table_name = table_name

    def get_company_year_tuples(self) -> list:
        try:
            response = self.client.table(self.table_name).select("Company, Year").execute()
        except Exception as e:
             Exception(f"Error fetching data from Supabase: {e}")
        print(response)

        
        rows = response.data
        # Build and return a list of (Company, Year) tuples.
        company_year_tuples = [
            (row['Company'], row['Year']) 
            for row in rows 
            if row.get('Company') is not None and row.get('Year') is not None
        ]
        return company_year_tuples

# Example usage:
if __name__ == "__main__":
    # Replace 'esg_data' with the actual table name if different.
    connector = SupabaseESGData(table_name="general_company_info_table")
    company_year_tuples = connector.get_company_year_tuples()
    print("Fetched (Company, Year) tuples:")
    print(company_year_tuples)