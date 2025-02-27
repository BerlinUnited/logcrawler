"""
    Backup of database and annotations
"""

from label_studio_sdk import Client
import time
import psycopg2
from os import environ
from pathlib import Path
from datetime import datetime
import subprocess

ls = Client(url=environ.get("LS_URL"), api_key=environ.get("LS_KEY"))
ls.check_connection()

# make this auto detect if its running inside the cluster or not
if "KUBERNETES_SERVICE_HOST" in environ:
    postgres_host = "postgres-postgresql.postgres.svc.cluster.local"
    postgres_port = 5432
else:
    postgres_host = "pg.berlin-united.com"
    postgres_port = 4000

params = {
    "host": postgres_host,
    "port": postgres_port,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get("DB_PASS"),
}
conn = psycopg2.connect(**params)
cur = conn.cursor()


def backup_annotations():
    """
    this should run every day eventually and upload the data to repl
    """
    backup_folder = Path(environ.get("BACKUPS_ROOT")) / "labelstudio_backups"
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d")
    current_backup_folder = backup_folder / Path(date_time)
    current_backup_folder.mkdir(exist_ok=True)

    existing_projects = ls.list_projects()
    for project in existing_projects:
        print(f"Exporting snapshot for project {project.id}")
        snapshot = project.export_snapshot_create(f"my_snapshot_{project.id}")
        while True:
            status_obj = project.export_snapshot_status(snapshot["id"])
            if status_obj.is_completed():
                project.export_snapshot_download(
                    export_id=snapshot["id"],
                    export_type="JSON",
                    path=str(current_backup_folder),
                )
                break
            if status_obj.is_failed():
                print("\tERROR: could not export snapshot")
                break
            time.sleep(1)


def backup_database():
    """
    restore goes like this:
    log into logcrawler pod go to folder containing the latest backup.sql and run psql -h pg.berlin-united.com -p 4000 -U naoth -W -d logs < backup.sql
    """
    backup_folder = Path(environ.get("BACKUPS_ROOT")) / "postgres_backups"
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d")
    current_backup_folder = backup_folder / Path(date_time)
    current_backup_folder.mkdir(exist_ok=True)

    output_file = current_backup_folder / Path("backup.sql")

    environ["PGPASSWORD"] = "fsdjhwzuertuqg"
    r = subprocess.run(
        "pg_dump -h pg.berlin-united.com -p 4000 -U naoth -d logs -Fp".split(),
        capture_output=True,
    )
    # print(r.stdout)
    with open(str(output_file), "w") as out:
        print(r.stdout.decode("utf-8"), file=out)


if __name__ == "__main__":
    backup_database()
    backup_annotations()
