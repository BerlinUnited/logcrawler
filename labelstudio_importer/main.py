"""
    Labelstudio importer
"""

import argparse
from os import environ
from pathlib import Path
from time import sleep

import psycopg2
import requests
from label_studio_sdk import Client

params = {
    "host": "pg.berlin-united.com",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get("DB_PASS"),
}
conn = psycopg2.connect(**params)
cur = conn.cursor()

if "KUBERNETES_SERVICE_HOST" in environ:
    LABEL_STUDIO_URL = "http://labelstudio-ls-app.labelstudio.svc.cluster.local"
else:
    LABEL_STUDIO_URL = "https://ls.berlin-united.com/"

API_KEY = "6cb437fb6daf7deb1694670a6f00120112535687"
ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()

label_config_bb = """
    <View>
        <Image name="image" value="$image" rotateControl="true"/>
        <RectangleLabels name="label" toName="image">
        <Label value="ball" background="#9eaeff"/><Label value="nao" background="#D4380D"/><Label value="penalty_mark" background="#e109da"/></RectangleLabels>
    </View>
    """


def get_logs_with_top_images():
    select_statement = f"""
    SELECT log_path, bucket_top FROM robot_logs WHERE bucket_top IS NOT NULL 
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]
    return logs


def get_new_logs_with_top_images():
    select_statement = f"""
    SELECT log_path, bucket_top FROM robot_logs WHERE bucket_top IS NOT NULL AND ls_project_top IS NULL
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]
    return logs


def get_logs_with_bottom_images():
    select_statement = f"""
    SELECT log_path, bucket_bottom FROM robot_logs WHERE bucket_bottom IS NOT NULL 
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]
    return logs


def get_new_logs_with_bottom_images():
    select_statement = f"""
    SELECT log_path, bucket_bottom FROM robot_logs WHERE bucket_bottom IS NOT NULL AND ls_project_bottom IS NULL
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]
    return logs


def import_labelstudio(data, camera):
    if camera == "top":
        color = "#D55C9D"  # pink
    else:
        color = "#51AAFD"  # blue

    existing_projects = [(a.title, a) for a in ls.list_projects()]
    existing_projects = dict(existing_projects)

    for logpath, bucketname in sorted(data, reverse=True):
        # FIXME rewrite the logic to not use the project name
        print(f"handling data from {logpath}")
        # generate description
        log_name = str(Path(logpath).name)
        game_name = str(Path(logpath).parent.parent.name)
        event_name = str(Path(logpath).parent.parent.parent.name)
        project_description = f"""
        event: {event_name} <br />
        game: {game_name} <br />
        log: {log_name}
        """

        if bucketname in existing_projects.keys():
            project_id = existing_projects[bucketname].id
            project = ls.get_project(project_id)
            print(f"\tproject {project_id} already exists")
            if camera == "top":
                insert_statement = f"""
                UPDATE robot_logs SET ls_project_top = '{project_id}' WHERE log_path = '{logpath}';
                """
            else:
                insert_statement = f"""
                UPDATE robot_logs SET ls_project_bottom = '{project_id}' WHERE log_path = '{logpath}';
                """

            project.set_params(**{"description": project_description})
            cur.execute(insert_statement)
            conn.commit()
            continue
        else:
            print(f"\tcreating project {bucketname}")
            project = ls.start_project(
                title=bucketname,
                label_config=label_config_bb,
                description=project_description,
                color=color,
            )
            import_storage = project.connect_s3_import_storage(
                bucket=bucketname,
                title=bucketname,
                aws_access_key_id="naoth",
                aws_secret_access_key="HAkPYLnAvydQA",
                s3_endpoint="https://minio.berlin-united.com",
            )
            if camera == "top":
                insert_statement = f"""
                UPDATE robot_logs SET ls_project_top = '{project.id}' WHERE log_path = '{logpath}';
                """
            else:
                insert_statement = f"""
                UPDATE robot_logs SET ls_project_bottom = '{project.id}' WHERE log_path = '{logpath}';
                """
            cur.execute(insert_statement)
            conn.commit()

            environ["TIMEOUT"] = "300"
            storage_id = import_storage["id"]
            # this function waits till storage is synchronized
            # TODO check closer what this does, docs imply the stream data from minio, but logs say something about copying
            # if data is just copied to a PVC then we dont need minio buckets for the images we can copy those from repl directly
            url = f"https://ls.berlin-united.com/api/storages/s3/{storage_id}/sync"
            while True:
                try:
                    x = requests.post(
                        url,
                        headers={
                            "Authorization": "Token 6cb437fb6daf7deb1694670a6f00120112535687"
                        },
                    )
                    print(f"\tsync status: {x.json()['status']}")
                    if x.json()["status"] == "completed":
                        break
                    else:
                        sleep(1)
                except:
                    print("\ttimeout on sync - should retry now")
                    sleep(1)


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

    data_top = (
        get_logs_with_top_images()
        if should_check_all
        else get_new_logs_with_top_images()
    )
    data_bottom = (
        get_logs_with_bottom_images()
        if should_check_all
        else get_new_logs_with_bottom_images()
    )

    import_labelstudio(data_top, "top")
    import_labelstudio(data_bottom, "bottom")
