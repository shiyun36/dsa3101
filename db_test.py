import os
from psycopg2 import pool
from dotenv import load_dotenv
# Load .env file
load_dotenv('secret.env')
# Get the connection string from the environment variable
connection_string = os.getenv('DATABASE_URL')

connection_pool = pool.SimpleConnectionPool(
    1,  # Minimum number of connections in the pool
    10,  # Maximum number of connections in the pool
    connection_string
)

if connection_pool:
    print("Connection pool created successfully")
# Get a connection from the pool
conn = connection_pool.getconn()

cur = conn.cursor()

with open('./db/db.sql','r',encoding="utf-8-sig") as file:
    create_db = file.read()
    cur.execute(create_db)
    conn.commit()