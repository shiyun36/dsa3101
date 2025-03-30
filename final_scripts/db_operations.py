import psycopg2
from db.scripts.batch_data_prepare_esg_rag_table import batch_data_prepare_esg_rag_table
from db.scripts.db_esg_rag_table_batch import insert_esg_rag_table_batch
from db.scripts.batch_data_prepare_esg_text import batch_data_prepare_esg_text
from db.scripts.db_esg_text_batch import insert_esg_text_batch

def insert_esg_rag_data(rag_df):
    esg_rag_df = batch_data_prepare_esg_rag_table(rag_df, batch_size=10)
    insert_esg_rag_table_batch(rag_df)
    print("ESG RAG data inserted into the esg_rag database successfully.")

def insert_esg_text_data(esg_text_df):
    esg_text_batch = batch_data_prepare_esg_text(esg_text_df, batch_size=100)
    insert_esg_text_batch(esg_text_batch)
    print("ESG text data inserted into the esg_text database successfully.")

def connect_to_database(database_url):
    try:
        conn = psycopg2.connect(database_url)
        print("Database connection established.")
        return conn
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None
