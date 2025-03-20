import psycopg2
import os
import json
from dotenv import load_dotenv


#Run
def insert_esg_vectorDB_batch(batch_data): #data_frame or text

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

    #get max doc_id and append a doc_id of the max + doc_id given (allows to insert new reports)
    ##empty##
    ##select_query
    query = '''
        INSERT INTO esg_vectorDB (doc_id, doc_text, metadatas)
        VALUES (%s, %s, %s)
    '''

    cur.executemany(query, batch_data)
    
    #commit to db
    conn.commit()

        #closes connection
    cur.close()
    conn.close()