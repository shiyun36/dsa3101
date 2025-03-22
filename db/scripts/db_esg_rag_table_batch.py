import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
import json

def insert_esg_rag_table_batch(batch_df):
    # Load environment variables
    load_dotenv('.env')
    
    # Get DB connection parameters
    db_name = os.getenv('db_name')
    db_user = os.getenv('db_user')
    db_port = os.getenv('db_port')
    db_host = os.getenv('db_host')
    db_password = os.getenv('db_password')

    ## SupaBase DB ##
    # db_url = os.getenv('DATABASE_URL')
    # conn = psycopg2.connect(db_url)


    # Connect to the database
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    
    # Create cursor
    cur = conn.cursor()

    # Define INSERT query
    query = '''
        INSERT INTO esg_rag_table (
            company, year, topic, extracted_values, final_score
        ) VALUES (%s, %s, %s, %s, %s)
    '''

    #insert in batch
    cur.executemany(query, batch_df)
    # Commit and close
    conn.commit()
    cur.close()
    conn.close()
