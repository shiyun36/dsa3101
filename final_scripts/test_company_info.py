from final_scripts.GeneralCompanyInfoProcessor import GeneralCompanyInfoProcessor
import os

def main():
    # Set test parameters.
    # Ensure that environment variables for API keys (e.g., GOOGLE_API_KEY and API_KEY) are set,
    # or set them in this file if needed.
    year = 2023
    company = "MORGANSTANLEY"
    output_csv = "./files/wiki/wiki_final.csv"  # Output CSV file
    saved_url_file = "./outputs"  # Make sure this directory exists or the code will create it

    # Create an instance of the GeneralCompanyInfoProcessor.
    processor = GeneralCompanyInfoProcessor(year=year,
                                             company=company,
                                             output_csv=output_csv,
                                             saved_url_file=saved_url_file)
    
    # Call a testing method to print the DataFrame structure.
    print("Testing the final_df preview:")
    processor.testing()
    
    # Call the method that uses OpenAI to query and then saves the results to the CSV.
    # This will trigger web search and OpenAI calls if the API keys are set.
    print("Running ask_openai_from_file() ...")
    processor.ask_openai_from_file()
    
    print("Test complete. Check the output CSV:", output_csv)

if __name__ == "__main__":
    main()