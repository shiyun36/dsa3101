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
cur.execute('CREATE TABLE esg_bert (sentence TEXT,label VARCHAR(255),score FLOAT);')
conn.commit()