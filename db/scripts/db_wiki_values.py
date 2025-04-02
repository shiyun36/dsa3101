import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
import json

def insert_wiki_df(df):
    # Load environment variables
    load_dotenv('.env')
    
    ## SupaBase DB ##
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    metrics = ['Company', 'Year', 'Country','Industry','GHG Scope 1 emission', 'GHG Scope 2 emission', 'GHG Scope 3 emission', 'Water Consumption', 'Energy Consumption', 'Waste Generation', 'Total Employees', 'Total Female Employees', 'Employees under 30', 'Employees between 30-50', 'Employees above 50s', 'Fatalities', 'Injuries', 'Avg Training Hours per employee' , 'Training Done, Independent Directors', 'Female Directors', 'Female Managers', 'Employees Trained', 'Certifications', 'Total Revenue', 'Total ESG Investment', 'Net Profit',' Debt-Equity Ratio', 'ROE', 'ROA']


    columns_str = ', '.join([f'"{col.strip()}"' for col in metrics])
    # Build a comma-separated string of placeholders.
    placeholders = ', '.join(['%s'] * len(metrics))

    # Create cursor
    cur = conn.cursor()

    # Define INSERT query
    query = f'''
        INSERT INTO general_company_info_table (
            {columns_str}
        ) VALUES ({placeholders})
    '''

    # Insert row-by-row
    for _, row in df.iterrows():
        # Build a tuple of values for the given metrics.
        # If needed, you can cast or transform certain values here.
        values = tuple(row[m] for m in metrics)
        print("Inserting row:", values)
        cur.execute(query, values)

    # Commit and close
    conn.commit()
    cur.close()