from final_scripts.WikiInforProcessor import CompanyInfoUpdater
import os
import pandas as pd

def main():
    # Set test parameters.
    csv_path = "./files/wiki/test_company_info.csv"  # Path to the local CSV file for processed data.
    
    # Create a dummy saved_url_df DataFrame.
    saved_url_df = pd.DataFrame({
        "URL": ["https://example.com/report1", "https://example.com/report2"],
        "Company": ["MORGANSTANLEY", "PUMAENERGY"],
        "Year": [2023, 2024]
    })

    # Create an input DataFrame with new company-year rows.
    input_df = pd.DataFrame({
        "Company": ["MORGANSTANLEY"],
        "Year": [2023],
        "Country": ["USA"],
        "Industry": ["Finance"],
    })

    # Instantiate the CompanyInfoUpdater with our test CSV path and saved_url_df.
    updater = CompanyInfoUpdater(saved_url_df=input_df)
    
    # Optionally, print existing CSV contents.
    if os.path.exists(csv_path):
        print("Existing CSV data:")
        print(pd.read_csv(csv_path))
    else:
        print("CSV file does not exist; it will be created.")

    # Call update_and_sync_supabase to update the CSV and get the missing rows.
    missing_rows_df = updater.form_supabase_input(input_df)
    
    print("\nMissing rows (to be inserted into Supabase):")
    print(missing_rows_df)
    

if __name__ == "__main__":
    main()