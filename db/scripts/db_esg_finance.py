import psycopg2
from dotenv import load_dotenv
import os
import json

def db_esg_ner(data_frame): #also outputs the company_name 
    load_dotenv()

    db_name = os.getenv('db_name')
    db_user = os.getenv('db_user')
    db_port = os.getenv('db_port')
    db_host = os.getenv('db_host')
    db_password = os.getenv('db_password')
    conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")

    # load_dotenv('secret.env')

    # db_name = os.getenv('db_name')
    # db_user = os.getenv('db_user')
    # db_port = os.getenv('db_port')
    # db_host = os.getenv('db_host')
    # db_password = os.getenv('db_password')
    # db_url = os.getenv('DATABASE_URL')
    # conn = psycopg2.connect(db_url)

    #create cursor & conn
    cur = conn.cursor()
    data_frame = data_frame.to_json(orient='records')
    js = json.loads(data_frame)
    #
    for row in js:
        print(row)
        cur.execute('''
                INSERT INTO esg_bert (
                    company, year, ticker, sentence,esg_cat, esg_subcat, confidence_score
                ) VALUES (%s, %s, %s,%s, %s, %s, %s)''', 
                (
                row["company"], 
                row["year"], 
                row["ticker"],
                row['sentence'],
                row["esg_cat"], 
                row["esg_subcat"], 
                row["score"],
            ))
    # for i in table_data_json:
    #     js_table = json.loads(i)
    #     for row in js_table:
    #         cur.execute('''
    #             INSERT INTO esg_bert (
    #                 company, year, sentence,esg_cat, esg_subcat, confidence_score, data_type
    #             ) VALUES (%s, %s, %s,%s, %s, %s, %s, %s)''', 
    #             (
    #             row["company"], 
    #             row["year"],
    #             row["ticker"], 
    #             row['sentence'],
    #             row["esg_cat"], 
    #             row["esg_subcat"], 
    #             row["confidence_score"],
    #             "table",
    #         ))
    
        #commit to db
    conn.commit()

        #closes connection
    cur.close()
    conn.close()
