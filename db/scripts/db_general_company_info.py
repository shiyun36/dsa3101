import psycopg2
import os
import json
from dotenv import load_dotenv
import pandas as pd


#Run
def insert_company_info(df): #data_frame or text
    #Load Env File
    load_dotenv('.env')
    
    #Get DB Params for Local DB
    db_name = os.getenv('db_name')
    db_user = os.getenv('db_user')
    db_port = os.getenv('db_port')
    db_host = os.getenv('db_host')
    db_password = os.getenv('db_password')
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    ## SupaBase DB ##
    # db_url = os.getenv('DATABASE_URL')
    # conn = psycopg2.connect(db_url)



    #create cursor & conn
    cur = conn.cursor()

    #get max doc_id and append a doc_id of the max + doc_id given (allows to insert new reports)

    query = '''
        INSERT INTO general_company_info_table (
            "Name", "Country", "Continent", "Industry", "Year",
            "GHG Scope 1 emission", "GHG Scope 2 emission", "GHG Scope 3 emission",
            "Water Consumption", "Energy Consumption", "Waste Generation",
            "Total Employees", "Total Female Employees", "Employees under 30",
            "Employees between 30-50", "Employees above 50s",
            "Fatalities", "Injuries", "Avg Training Hours per employee",
            "Training Done, Independent Directors", "Female Directors", "Female Managers",
            "Employees Trained", "Certifications", "Total Revenue", "Total ESG Investment",
            "Net Profit", "Debt-Equity Ratio", "ROE", "ROA"
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        ON CONFLICT ("Name", "Year") DO NOTHING;
        '''
    
    for _, row in df.iterrows():
        cur.execute(query, (
            row["Name"], row["Country"], row["Continent"], row["Industry"], row["Year"],
            row["GHG Scope 1 emission"], row["GHG Scope 2 emission"], row["GHG Scope 3 emission"],
            row["Water Consumption"], row["Energy Consumption"], row["Waste Generation"],
            row["Total Employees"], row["Total Female Employees"], row["Employees under 30"],
            row["Employees between 30-50"], row["Employees above 50s"],
            row["Fatalities"], row["Injuries"], row["Avg Training Hours per employee"],
            row["Training Done, Independent Directors"], row["Female Directors"], row["Female Managers"],
            row["Employees Trained"], row["Certifications"], row["Total Revenue"], row["Total ESG Investment"],
            row["Net Profit"], row["Debt-Equity Ratio"], row["ROE"], row["ROA"]
        ))
    
    #commit to db
    conn.commit()

    #closes connection
    cur.close()
    conn.close()