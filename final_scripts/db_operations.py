import psycopg2
from db.scripts.db_esg_rag_table import insert_esg_rag_table
from db.scripts.db_esg_text import insert_esg_text

def insert_esg_rag_data(rag_df):
    insert_esg_rag_table(rag_df)
    print("ESG RAG data inserted into the esg_rag database successfully.")

def insert_esg_text_data(esg_text_df):
    insert_esg_text(esg_text_df)
    print("ESG text data inserted into the esg_text database successfully.")

def connect_to_database(database_url):
    try:
        conn = psycopg2.connect(database_url)
        print("Database connection established.")
        return conn
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None