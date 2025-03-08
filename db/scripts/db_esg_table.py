import psycopg2
from dotenv import load_dotenv
import os
import json


def db_esg_table(table_data_json, company,year,ticker): #also outputs the company_name 

    load_dotenv()

    db_name = os.getenv('db_name')
    db_user = os.getenv('db_user')
    db_port = os.getenv('db_port')
    db_host = os.getenv('db_host')
    db_password = os.getenv('db_password')
    #create cursor & conn
    conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")
    cur = conn.cursor()
    
    
    for i in table_data_json:
        # js_table = json.loads(i)
        table_data = {
            'company': company,
        'year' : year,
        'ticker': ticker,
        'json_table' : f"{json.loads(i)}"
        }
        print(table_data)
    
        cur.execute('''
            INSERT INTO esg_table_data (
                    company, year, ticker,json_table
                ) VALUES (%s, %s, %s,%s)''', 
            (
            table_data["company"], 
            table_data["year"],
            table_data["ticker"], 
            table_data['json_table'],
            ))
    
    conn.commit()

        #closes connection
    cur.close()
    conn.close()
