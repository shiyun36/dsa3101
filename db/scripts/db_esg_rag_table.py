import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
import json

def insert_esg_rag_table(df):
    # Load environment variables
    load_dotenv('.env')
    
    # Get DB connection parameters
    # db_name = os.getenv('db_name')
    # db_user = os.getenv('db_user')
    # db_port = os.getenv('db_port')
    # db_host = os.getenv('db_host')
    # db_password = os.getenv('db_password')
    # conn = psycopg2.connect(
    #     dbname=db_name,
    #     user=db_user,
    #     password=db_password,
    #     host=db_host,
    #     port=db_port
    # )

    ## SupaBase DB ##
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url)


    # Connect to the database
    
    # Create cursor
    cur = conn.cursor()

    # Define INSERT query
    query = '''
        INSERT INTO esg_rag_table (
            company, industry, country, year, topic, extracted_values, final_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (company, industry, country,year,topic,extracted_values,final_score) DO NOTHING;
    '''

    # Insert row-by-row
    for _, row in df.iterrows():
        print(row)
        cur.execute(query, (
            row["company"],
            row['industry'],
            row['country'],
            int(row["year"]),
            row["topic"],
            json.dumps(row["extracted_values"]),  # Convert dict to JSON string
            None if pd.isna(row["final_score"]) else float(row["final_score"])
        ))

    # Commit and close
    conn.commit()
    cur.close()
    conn.close()
