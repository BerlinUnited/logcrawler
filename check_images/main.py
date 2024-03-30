"""
    Check if images exist
"""

from pathlib import Path
import psycopg2
from os import environ
import json

params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get('DB_PASS')
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


if __name__ == "__main__":
    root_path = Path(environ.get("LOG_ROOT"))
    log_list = get_logs()

    for log_folder in log_list:
        print(log_folder)
        actual_log_folder = root_path / Path(log_folder)
        representation_file = actual_log_folder / "representation.json"

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

