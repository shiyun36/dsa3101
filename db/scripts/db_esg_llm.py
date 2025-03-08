import psycopg2
from dotenv import load_dotenv
import os
import json




def db_esg_llm(clean_llm_output_list): #also outputs the company_name 
    load_dotenv()

    db_name = os.getenv('db_name')
    db_user = os.getenv('db_user')
    db_port = os.getenv('db_port')
    db_host = os.getenv('db_host')
    db_password = os.getenv('db_password')
    #create cursor & conn
    conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")
    cur = conn.cursor()
    #
    for i in clean_llm_output_list:
        js = json.loads(i)
        print(js)

        #inserts each row into the db in esg_llm
        for row in js:
            cur.execute('''
                INSERT INTO esg_llm (
                    company, year, ticker,industry, esg_category, esg_subcategory, sentence_type, 
                    esg_framework, raw_score, esg_risk_prediction, summarized_sentences_data, relevance_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                (
                row["company"], 
                row["year"], 
                row['ticker'],
                row["industry"], 
                row["esg_category"], 
                row["esg_subcategory"],
                row["sentence_type"],
                row["esg_framework"], 
                row["raw_score"], 
                row["esg_risk_prediction"], 
                row["summarized_sentences_data"], 
                row["relevance_score"]
            ))
        #commit to db
    conn.commit()
        #closes connection
    cur.close()
    conn.close()
