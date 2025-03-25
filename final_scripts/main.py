import argparse
import os
from dotenv import load_dotenv
from PdfExtractor import PDFExtractor
from ../extractValues import RAG
from db_operations import connect_to_database, insert_esg_rag_data, insert_esg_text_data
from financial import financial
from GeneratePdfs import GeneratePdfs
from ESGScoringProcessor import ESGScoringProcessor

def main():
    # Setup argparse to receive the URL
    parser = argparse.ArgumentParser(description="Extract ESG data from a PDF report URL")
    parser.add_argument("--url", type=str, help="PDF URL of the sustainability report")
    parser.add_argument("--country", type=str, help="Country the company is based in")
    parser.add_argument("--industry", type=str, help="Industry the company belongs to")
    args = parser.parse_args()

    load_dotenv()  # Loads .env from the project root
    API_KEY = os.getenv("API_KEY")

    # If run without CLI args, fallback to defaults
    if not any(vars(args).values()):
        args.url = "https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/ocbc-sustainability-report-2023.pdf"
        args.country = "singapore"
        args.industry = "finance"

    # Database connection string
    DATABASE_URL = os.getenv("DATABASE_URL")  # Use environment variables for sensitive info

    # Connect to the database
    conn = connect_to_database(DATABASE_URL)
    if conn:
        # Step 0: Generate pdf links that will be extracted 
        pdf_links_generator = GeneratePdfs()
        pdf_links_generator.run()
        
        # Step 1: Extract ESG text
        pdf_extractor = PDFExtractor(saved_url_file, country, industry)
        esg_text_df = pdf_extractor.process_pdf()
        if esg_text_df.empty:
            print("No ESG text extracted. Skipping processing.")
        else:
            ## process esg text for RAG
            esg_processor = ESGScoringProcessor(esg_text_df)
            result_df = processor.convert_to_esg_rag_dataframe()
            
            # Step 2: Process RAG
            rag_df = RAG.rag_main(result_df)

            # Step 3: Insert data into database
            insert_esg_rag_data(rag_df)
            insert_esg_text_data(esg_text_df)

            # Step 4: Call financial function to insert financial data into database 
            financial() 

        # Close the connection
        conn.close()

if __name__ == "__main__":
    main()
