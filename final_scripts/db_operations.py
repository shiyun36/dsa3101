import psycopg2
from db.scripts.db_esg_rag_table import insert_esg_rag_table
from db.scripts.db_esg_text import insert_esg_text
from db.scripts.db_wiki_values import insert_wiki_df

def insert_esg_rag_data(rag_df):
    insert_esg_rag_table(rag_df)
    print("ESG RAG data inserted into the esg_rag database successfully.")

def insert_esg_text_data(esg_text_df):
    insert_esg_text(esg_text_df)
    print("ESG text data inserted into the esg_text database successfully.")

def insert_wiki_data(wiki_df):
    insert_wiki_df(wiki_df)
    print("Wikidata inserted into the wiki database successfully.")
    
def connect_to_database(database_url):
    try:
        conn = psycopg2.connect(database_url)
        print("Database connection established.")
        return conn
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None