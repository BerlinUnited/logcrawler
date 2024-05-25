"""
    Check if images exist
"""

from pathlib import Path
import psycopg2
from os import environ
import json
import argparse

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


def get_logs():
    select_statement = f"""
    SELECT log_path FROM robot_logs WHERE broken = False
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x[0] for x in rtn_val]
    return logs


def get_unchecked_logs():
    select_statement = f"""
    SELECT log_path FROM robot_logs WHERE images_exist IS NULL
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x[0] for x in rtn_val]
    return logs


if __name__ == "__main__":
    # add argument parser to select which logs to check
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all",
        help="Check all logs, by default only unchecked logs are checked",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    should_check_all = args.all

    root_path = Path(environ.get("LOG_ROOT"))
    log_list = get_logs() if should_check_all else get_unchecked_logs()

    for log_folder in sorted(log_list, reverse=True):
        print(log_folder)
        log_path_w_prefix = root_path / Path(log_folder)
        if Path(log_path_w_prefix).is_file():
            actual_log_folder = root_path / Path(log_folder).parent
            representation_file = actual_log_folder / str(
                Path(log_folder).name + ".representation.json"
            )
        else:
            actual_log_folder = root_path / Path(log_folder)
            representation_file = actual_log_folder / "representation.json"

        if representation_file.exists():
            with open(str(representation_file), "r", encoding="utf-8") as f:
                data = json.load(f)

            representations = data["representations"]
            if "Image" in representations or "ImageTop" in representations:
                print("\tfound images")
                # write to db
                insert_statement = f"""
                UPDATE robot_logs SET images_exist = true WHERE log_path = '{log_folder}';
                """
                cur.execute(insert_statement)
                conn.commit()
            else:
                # write to db
                insert_statement = f"""
                UPDATE robot_logs SET images_exist = false WHERE log_path = '{log_folder}';
                """
                cur.execute(insert_statement)
                conn.commit()
