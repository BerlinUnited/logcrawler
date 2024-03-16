"""
    Labelstudio importer
"""

import sys
from pathlib import Path
from label_studio_sdk import Client
from minio import Minio
import psycopg2
import random
import string
import requests
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
label_config_bb = """
    <View>
        <Image name="image" value="$image" rotateControl="true"/>
        <RectangleLabels name="label" toName="image">
        <Label value="ball" background="#9eaeff"/><Label value="nao" background="#D4380D"/><Label value="penalty_mark" background="#e109da"/></RectangleLabels>
    </View>
    """


def get_logs_with_top_images():
    select_statement = f"""
    SELECT log_path,bucket_top  FROM robot_logs WHERE bucket_top IS NOT NULL 
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]
    print(logs)
    return logs


def get_logs_with_bottom_images():
    select_statement = f"""
    SELECT log_path FROM robot_logs WHERE bucket_bottom IS NOT NULL 
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]

    return logs


if __name__ == "__main__":
    """
    something like give the logpath as argument and then this code checks if its already done
    """
    # TODO use argparse here
    root_path = (
        environ.get("LOG_ROOT") or "/mnt/q/"
    )  # use or with environment variable to make sure it works in k8s as well
    root_path = Path(root_path)

    data_top = get_logs_with_top_images()
    for logpath, bucketname in data_top:
        print(bucketname)
        existing_projects = [a.title for a in ls.list_projects()]
        if bucketname in existing_projects:
            print("project already exists")
            continue
        else:
            project = ls.start_project(
                title=bucketname, label_config=label_config_bb, description=logpath
            )
            rt_val = project.connect_s3_import_storage(
                bucket=bucketname,
                title=bucketname,
                aws_access_key_id="naoth",
                aws_secret_access_key="HAkPYLnAvydQA",
                s3_endpoint="https://minio.berlinunited-cloud.de",
            )
            storage_id = rt_val["id"]
            print(rt_val)
            project.sync_import_storage(rt_val["type"], storage_id)

            quit()
        
    log_list_bottom = get_logs_with_bottom_images()
    quit()
    # for log_folder in log_list_top:
    # TODO build a better parser that can get all the information out of the path name
    log_name = str(Path(log_folder).name).replace("_", ".")
    game_name = str(Path(log_folder).parent.parent.name).replace("_", ".")
    event_name = str(Path(log_folder).parent.parent.parent.name).replace("_", ".")

    project_name_bottom = event_name + "." + game_name + "." + log_name + ".bottom"
    project_name_top = event_name + "." + game_name + "." + log_name + ".top"

    bottom_data = Path(log_folder) / Path("combined_bottom")
    top_data = Path(log_folder) / Path("combined_top")

    bucket_name_bottom = create_bucket_from_logfile(bottom_data)
    bucket_name_top = create_bucket_from_logfile(top_data)

    create_project_if_not_exists("RC23-Hulks-half1-nao24-bottom", bucket_name_bottom)
    create_project_if_not_exists("RC23-Hulks-half1-nao24-top", bucket_name_top)
