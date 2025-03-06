import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

db_name = os.getenv('db_name')
db_user = os.getenv('db_user')
db_port = os.getenv('db_port')
db_host = os.getenv('db_host')
db_password = os.getenv('db_password')

conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")
cur = conn.cursor()

#Create database in psql with the tables
with open('./db/db.sql','r',encoding="utf-8-sig") as file:
    create_db = file.read()
    cur.execute(create_db)
    conn.commit()

# #Example data population
# with open('./example_db_data/example_db_data pfizer_2024.csv', 'r', encoding='utf-8') as file:
#     cs = csv.reader(file, )
#     next(cs) #Goes to the next row(Skip headers)
#     for row in cs:
#         cur.execute(''' 
#                     INSERT INTO esg_bert (esg_cat,sentence,confidence_score)
#                     VALUES (%s, %s,%s)                
# ''', (row[1],row[2],row[3]))
#     conn.commit()
        
cur.close()
conn.close()
