"""
"""
import pathlib
import time
import psycopg2

params = {"host": "postgres.postgres","port": 5432,"dbname": "postgres","user": "postgres","password": "123"}
conn = psycopg2.connect(**params)
cur = conn.cursor()

cur.execute("SELECT version()")
version = cur.fetchone()
print(f"Postgres version: {version}")

# folder path
dir_path = '/mnt/repl/'
# construct path object
d = pathlib.Path(dir_path)

while True:
    # iterate directory
    for entry in d.iterdir():
        # check if it a file
        print(entry)

    time.sleep(5)