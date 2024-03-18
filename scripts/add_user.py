"""
    Labelstudio importer
"""
from pathlib import Path
from label_studio_sdk import Client, users
from minio import Minio
import psycopg2
from os import environ

params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": "fsdjhwzuertuqg",
}
conn = psycopg2.connect(**params)
cur = conn.cursor()


LABEL_STUDIO_URL = "https://ls.berlinunited-cloud.de/"
API_KEY = "6cb437fb6daf7deb1694670a6f00120112535687"
ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()

if __name__ == "__main__":
    print(ls.get_users())
    #ls.create_user({'username':'label_bot', 'email':'bot@berlinunited.com', 'first_name':'eliza', 'last_name':'bot'}, exist_ok=True)
