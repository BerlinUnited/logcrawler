"""
"""
import pathlib
import time
import psycopg2

# connect to database
params = {"host": "postgres.postgres","port": 5432,"dbname": "postgres","user": "postgres","password": "123"}
conn = psycopg2.connect(**params)
cur = conn.cursor()

cur.execute("SELECT version()")
version = cur.fetchone()
print(f"Postgres version: {version}")

while True:
    print(f"Postgres version: {version}")
    time.sleep(5)