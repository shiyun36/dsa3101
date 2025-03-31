import psycopg2
import os
import json
from dotenv import load_dotenv
import pandas as pd


#Run
def insert_model_lr(results_df,df_rfe): #data_frame or text
    #Load Env File
    load_dotenv('.env')
    
    #Get DB Params for Local DB
    # db_name = os.getenv('db_name')
    # db_user = os.getenv('db_user')
    # db_port = os.getenv('db_port')
    # db_host = os.getenv('db_host')
    # db_password = os.getenv('db_password')
    # conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")

    ## SupaBase DB ##
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url)

    #create cursor & conn
    cur = conn.cursor()

    ##refresh values
    cur.execute("DELETE FROM esg_financial_model_top_features_table") #delete all rows in table because should reset everytime model is run
    cur.execute("DELETE FROM esg_financial_model_top_features_table") #delete all rows in table because should reset everytime model is run
    ##

    ## for results_df
    query_results = '''
                INSERT INTO esg_financial_model_table (
                    esg_score, roa_actual, roa_predicted, roe_actual,roe_predicted,stock_growth_actual,stock_growth_predicted
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
    
    for _,row in results_df.iterrows():
        cur.execute(query_results, (row['ESG_Score'], row['ROA_Actual'], row['ROA_Predicted'], row['ROE_Actual'], row['ROE_Predicted'], row['Stock_Growth_Actual'], row['Stock_Growth_Predicted']))
    ## for df_rfe
    query = '''
            INSERT INTO esg_financial_model_top_features_table (
                variable, feature, rank
            ) VALUES (%s, %s, %s)
          '''
    for _,row in df_rfe.iterrows():
        cur.execute(query, (row['Target Variable'], row['Feature'], row['Rank']))

    #commit to db
    conn.commit()

    #closes connection
    cur.close()
    conn.close()