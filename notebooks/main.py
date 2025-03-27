import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
import psycopg2
from dotenv import load_dotenv
from extract_text_company_year import extract_text_company_year
from convert_scoring_metric_to_esg_rag_dataframe import convert_scoring_metric_to_esg_rag_dataframe
from db.scripts.batch_data_prepare_esg_rag_table import batch_data_prepare_esg_rag_table
from db.scripts.db_esg_rag_table_batch import insert_esg_rag_table_batch
from db.scripts.db_esg_rag_table import insert_esg_rag_table
from db.scripts.db_esg_text import insert_esg_text
from extractValues import RAG
from financial import financial


def extract_url_to_esg_rag_database(url, country, industry):
    print(f"Extracting ESG text from: {url}")
    
    # Extract ESG-related text and metadata from the url
    df = extract_text_company_year(url, country, industry)
    esg_text_df = df[["company", "year", "country", "industry", "esg_text"]]
    
    if df.empty:
        print("No text extracted. Skipping database insertion.")
        return
    
    # Returning a dataframe containing the extracted values and esg metric scores by using RAG and LLM
    rag_csv_path = RAG.rag_main(df)

    # Converting RAG dataframe to match esg_rag_table schema
    esg_rag_df = convert_scoring_metric_to_esg_rag_dataframe(rag_csv_path)

    # Inserting esg text into esg_text_table database
    insert_esg_text(esg_text_df)
    print("ESG text data inserted into the esg_text database successfully.")

    financial()
    print("Successfully run financial")

    # Insert esg rag results into esg_rag_table database
    insert_esg_rag_table(esg_rag_df)
    print("ESG RAG data inserted into the esg_rag database successfully.")



def main():
    # Setup argparse to receive the URL
    parser = argparse.ArgumentParser(description = "Extract ESG data from a PDF report URL")
    parser.add_argument("--url", type = str, help = "PDF URL of the sustainability report")
    parser.add_argument("--country", type = str, help = "Country the company is based in")
    parser.add_argument("--industry", type = str, help = "Industry the company belongs to")
    args = parser.parse_args()

    load_dotenv()  # Loads .env from the project root


    # (CHANGE ARGUMENTS HERE) If run without CLI args (e.g., directly in a script), fallback to defaults
    if not any(vars(args).values()):
        args.url = "https://sustainability.pertamina.com/en-US/Reports-and-Publications/Sustainability-Report/Sustainability-Report-2023.pdf"
        args.country = "indonesia"
        args.industry = "energy"

    
    # Database connection string
    DATABASE_URL = "postgresql://postgres.pevfljfvkiaokawnfwtb:7EzzdSDKIcrQwzlf@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Database connection established.")

        extract_url_to_esg_rag_database(args.url, args.country, args.industry)

        conn.close()

    except Exception as e:
        print(f"Failed to connect to database or run pipeline: {e}")

if __name__ == "__main__":
    main()