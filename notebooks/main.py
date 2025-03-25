import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import os
import argparse
import psycopg2
from dotenv import load_dotenv
from extract_text_company_year import extract_text_company_year
from convert_scoring_metric_to_esg_rag_dataframe import convert_scoring_metric_to_esg_rag_dataframe
from db.scripts.batch_data_prepare_esg_rag_table import batch_data_prepare_esg_rag_table
from db.scripts.db_esg_rag_table_batch import insert_esg_rag_table_batch
from db.scripts.batch_data_prepare_esg_text import batch_data_prepare_esg_text
from db.scripts.db_esg_text_batch import insert_esg_text_batch
from  extractValues import RAG



def extract_url_to_esg_rag_database(url, country, industry, conn):
    print(f"Extracting ESG text from: {url}")
    
    # Extract ESG-related text and metadata from the url
    df = extract_text_company_year(url, country, industry)
    esg_text_df = df[["company", "year", "country", "industry", "esg_text"]]
    
    if df.empty:
        print("No text extracted. Skipping database insertion.")
        return
    print(str(df))
    # Returning a dataframe containing the extracted values and esg metric scores by using RAG and LLM
    rag_df = RAG.rag_main(df)

    # Converting RAG dataframe to match esg_rag_table schema
    esg_rag_df = convert_scoring_metric_to_esg_rag_dataframe(rag_df)

    # Insert esg rag results into esg_rag_table database
    esg_rag_batch = batch_data_prepare_esg_rag_table(esg_rag_df, batch_size = 10)
    insert_esg_rag_table_batch(rag_df)
    print("ESG RAG data inserted into the esg_rag database successfully.")

    # Inserting esg text into esg_text_table database
    esg_text_batch = batch_data_prepare_esg_text(esg_text_df, batch_size = 100)
    insert_esg_text_batch(esg_text_batch)
    print("ESG text data inserted into the esg_text database successfully.")

def main():
    # Setup argparse to receive the URL
    parser = argparse.ArgumentParser(description="Extract ESG data from a PDF report URL")
    parser.add_argument("--url", type = str, help = "PDF URL of the sustainability report")
    parser.add_argument("--country", type = str, help = "Country the company is based in")
    parser.add_argument("--industry", type = str, help = "Industry the company belongs to")
    args = parser.parse_args()

    load_dotenv()  # Loads .env from the project root

    API_KEY = os.getenv("API_KEY")

    # (CHANGE ARGUMENTS HERE) If run without CLI args (e.g., directly in a script), fallback to defaults
    if not any(vars(args).values()):
        args.url = "https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/ocbc-sustainability-report-2023.pdf"
        args.country = "singapore"
        args.industry = "finance"

    
    # Database connection string
    DATABASE_URL = "postgresql://postgres.pevfljfvkiaokawnfwtb:7EzzdSDKIcrQwzlf@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Database connection established.")

        extract_url_to_esg_rag_database(args.url, args.country, args.industry, conn)

        conn.close()

    except Exception as e:
        print(f"Failed to connect to database or run pipeline: {e}")

if __name__ == "__main__":
    main()