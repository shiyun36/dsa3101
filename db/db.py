import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

db_name = os.getenv('db_name')
db_user = os.getenv('db_user')
db_port = os.getenv('db_port')
db_host = os.getenv('db_host')
db_password = os.getenv('db_password')


#Database creation script

# load_dotenv('secret.env')

# db_name = os.getenv('db_name')
# db_user = os.getenv('db_user')
# db_port = os.getenv('db_port')
# db_host = os.getenv('db_host')
# db_password = os.getenv('db_password')
# db_url = os.getenv('DATABASE_URL')

########### LOCAL DB #################
conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")
cur = conn.cursor()

#Create database in psql with the tables
with open('./db/db.sql','r',encoding="utf-8-sig") as file:
    create_db = file.read()
    cur.execute(create_db)
    
conn.commit()

cur.close()
conn.close()

######### Online Hosted DB #################
##Direct connection to supabase online-hosted
# conn = psycopg2.connect(db_url)
# cur = conn.cursor()
# #Create database in psql with the tables
# with open('./db/db.sql','r',encoding="utf-8-sig") as file:
#     create_db = file.read()
#     cur.execute(create_db)
#     conn.commit()

# conn.commit()
# cur.close()
# conn.close()