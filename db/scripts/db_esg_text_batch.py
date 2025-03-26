import psycopg2
import os
import json
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

def insert_function(batch_data):
    #Load Env File
    load_dotenv('.env')

    #Get DB Params for Local DB
    db_name = os.getenv('db_name')
    db_user = os.getenv('db_user')
    db_port = os.getenv('db_port')
    db_host = os.getenv('db_host')
    db_password = os.getenv('db_password')
    conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")

    ## SupaBase DB ##
    # db_url = os.getenv('DATABASE_URL')
    # conn = psycopg2.connect(db_url)

    #create cursor & conn
    cur = conn.cursor()

    query = '''INSERT INTO esg_text_table (
                    company, year, country, industry,esg_text
                ) VALUES (%s, %s, %s,%s, %s)
                ON CONFLICT (company, year, country,industry,esg_text) DO NOTHING;'''

    #execute query on a batch of data from DF
    cur.executemany(query, batch_data)

    #commit to db
    conn.commit()

        #closes connection
    cur.close()
    conn.close()

def insert_esg_text_batch(batch_data): #data_frame or text
    with ProcessPoolExecutor() as executor: #allows for parallel processing
        list(tqdm(executor.map(insert_function,batch_data), total=len(batch_data), desc='Insert batches into DB', unit='batch', ncols=100))