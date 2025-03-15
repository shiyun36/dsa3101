import psycopg2
import os
import json
from dotenv import load_dotenv
import pandas as pd


#Run
def insert_region_table(): #data_frame or text

    df = pd.read_csv('country_regions.csv')
    #Load Env File
    load_dotenv('.env')
    #Get DB Params for Local DB
    # db_name = os.getenv('db_name')
    # db_user = os.getenv('db_user')
    # db_port = os.getenv('db_port')
    # db_host = os.getenv('db_host')
    # db_password = os.getenv('db_password')
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    # conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")

    ## SupaBase DB ##
    # db_url = os.getenv('DATABASE_URL')
    # conn = psycopg2.connect(db_url)

    #create cursor & conn
    cur = conn.cursor()

    #get max doc_id and append a doc_id of the max + doc_id given (allows to insert new reports)

    query = '''
            INSERT INTO region_table (
                country, region, subregion
            ) VALUES (%s, %s, %s)'''
    for _, row in df.iterrows():
            cur.execute(query, (row["country"], row["region"], row["subregion"]))
    
    #commit to db
    conn.commit()

    #closes connection
    cur.close()
    conn.close()
insert_region_table()