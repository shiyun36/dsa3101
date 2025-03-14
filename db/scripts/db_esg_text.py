import psycopg2
import os
import json
from dotenv import load_dotenv

def insert_esg_text(data_frame): #data_frame or text

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

    ##converts data_frame to json format
    data_frame = data_frame.to_json(orient='records')

    #json loader
    js = json.loads(data_frame)

    #
    for row in js:
        print(row)
        print(row['country'])
        cur.execute('''
                INSERT INTO esg_text_table (
                    company, year, country, industry,esg_text, labels
                ) VALUES (%s, %s, %s,%s, %s, %s)''', 
                (
                row["company"], 
                row["year"], 
                row["country"],
                row['industry'],
                row["esg_text"], 
                row["labels"],
            ))
    
    #commit to db
    conn.commit()

        #closes connection
    cur.close()
    conn.close()