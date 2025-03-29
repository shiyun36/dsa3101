# import argparse
import os
from dotenv import load_dotenv
from PdfExtractor import PDFExtractor
from ..notebooks.extractValues.RAG import RAG
from db_operations import connect_to_database, insert_esg_rag_data, insert_esg_text_data
from ..notebooks.financial import financial
from GeneratePdfs import GeneratePdfs
from ESGScoringProcessor import RagScoreProcessor
# from RAGProcessor import RAGProcessor

# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# DATABASE_URL = os.getenv("DATABASE_URL")
# GPT_API_KEY = os.getenv("GPT_API_KEY") ##If changing RAG to class, can input GPT_API_KEY in the variables. 
DATABASE_URL = "postgresql://postgres.pevfljfvkiaokawnfwtb:7EzzdSDKIcrQwzlf@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
URL_OUTPUT_FILE="../outputs/pdf_links.txt"

########### ADJUST YOUR INPUTS HERE #############
COUNTRY = 'singapore'
INDUSTRY = 'health'
YEARS = [2024, 2023, 2022, 2021]
INSERT_URL = "https://investor.econhealthcare.com/misc/sr2024.pdf"
#################################################


def main():
    # Setup argparse to receive the URL
    # parser = argparse.ArgumentParser(description="Extract ESG data from a PDF report URL")
    # parser.add_argument("--url", type=str, help="PDF URL of the sustainability report")
    # parser.add_argument("--country", type=str, help="Country the company is based in")
    # parser.add_argument("--industry", type=str, help="Industry the company belongs to")
    # args = parser.parse_args()

    # # If run without CLI args, fallback to defaults
    # if not any(vars(args).values()):
    #     args.url = "https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/ocbc-sustainability-report-2023.pdf"
    #     args.country = "singapore"
    #     args.industry = "finance"

    # Database connection string
      # Use environment variables for sensitive info

    # Connect to the database
    conn = connect_to_database(DATABASE_URL)
    if conn:
        if INSERT_URL == "":
        
            ##### Step 0: Generate pdf links that will be extracted  #####
            pdf_links_generator = GeneratePdfs(output_file=URL_OUTPUT_FILE, 
                                            log_file = "../loggings/pdf_scraper.log",
                                            years =YEARS,
                                            industry = INDUSTRY, 
                                            country = COUNTRY,
                                            GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")) 
            pdf_links_generator.run()
            ##### Step 1: Extract ESG text from pdf links #####
            pdf_extractor = PDFExtractor(saved_url_file = URL_OUTPUT_FILE, 
                                        insert_url = INSERT_URL,
                                        country = COUNTRY, 
                                        industry = INDUSTRY)
            esg_text_df = pdf_extractor.process_pdf()
        
        else:
            ##### Step 1: Extract ESG text from pdf links #####
            pdf_extractor = PDFExtractor(saved_url_file = URL_OUTPUT_FILE, 
                                        insert_url = INSERT_URL,
                                        country = COUNTRY, 
                                        industry = INDUSTRY)
            esg_text_df = pdf_extractor.process_pdf()
        
        
        if esg_text_df.empty:
            print("No ESG text extracted. Skipping processing.")
        else:
            
            ##### Step 2: Process RAG #####
            rag_csv_path = RAG.rag_main(esg_text_df)

            # Converting RAG dataframe to match esg_rag_table schema
            rag_score_processor = RagScoreProcessor(rag_csv_path)
            esg_rag_df = rag_score_processor.convert_to_esg_rag_dataframe()

            ##### Step 3: Insert data into database #####
            insert_esg_rag_data(esg_rag_df)
            insert_esg_text_data(esg_text_df)

            ##### Step 4: Call financial function to insert financial data into database #####
            financial() 

        # Close the connection
        conn.close()

if __name__ == "__main__":
    main()
