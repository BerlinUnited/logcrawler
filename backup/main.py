"""
    Backup of database and annotations
"""
from label_studio_sdk import Client
import time
import psycopg2
from os import environ

ls = Client(url=environ.get('LS_URL'), api_key=environ.get('LS_KEY'))
ls.check_connection()

params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get('DB_PASS'),
}
conn = psycopg2.connect(**params)
cur = conn.cursor()


def backup_annotations():
    """
        this should run every day eventually and upload the data to repl
    """
    existing_projects = ls.list_projects()
    for project in existing_projects:
        print(f"Exporting snapshot for project {project}")
        snapshot = project.export_snapshot_create(f"my_snapshot_{project.id}")
        while True:       
            status_obj = project.export_snapshot_status(snapshot["id"])
            print(status_obj.response)
            if status_obj.is_completed():
                # TODO download to a folder and then upload the folder or mount backup directly
                project.export_snapshot_download(snapshot["id"])
                break
            if status_obj.is_failed():
                print("\tERROR: could not export snapshot")
                break
            time.sleep(1)
        break


def backup_database():
    import subprocess
    import os
    os.environ["PGPASSWORD"] = "fsdjhwzuertuqg"
    r = subprocess.run("pg_dump -h pg.berlinunited-cloud.de -p 4000 -U naoth -d logs -Fp".split(), capture_output=True)
    #print(r.stdout)
    with open("backup.sql", 'w') as out:
        print(r.stdout.decode('utf-8'), file=out)


if __name__ == "__main__":
    backup_database()