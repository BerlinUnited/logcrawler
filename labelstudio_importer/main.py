"""
    Labelstudio importer
"""
from pathlib import Path
from label_studio_sdk import Client
import psycopg2
from os import environ
import time
import datetime

params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get('DB_PASS')
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
    SELECT log_path,bucket_top FROM robot_logs WHERE bucket_top IS NOT NULL 
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

def import_labelstudio(data, color):
    existing_projects = [a.title for a in ls.list_projects()]
    for logpath, bucketname in data:
        print(f"handling data from {logpath}")
        if bucketname in existing_projects:
            print("\tproject already exists")
            continue
        else:
            log_name = str(Path(logpath).name)
            game_name = str(Path(logpath).parent.parent.name)
            event_name = str(Path(logpath).parent.parent.parent.name)
            description = f"""
            event: {event_name} < /br>
            game: {game_name} < /br>
            log: {log_name}
            """
            print(f"\tcreating project {bucketname}")
            project = ls.start_project(
                title=bucketname,
                label_config=label_config_bb,
                description=description,
                color=color
            )
            import_storage = project.connect_s3_import_storage(
                bucket=bucketname,
                title=bucketname,
                aws_access_key_id="naoth",
                aws_secret_access_key="HAkPYLnAvydQA",
                s3_endpoint="https://minio.berlinunited-cloud.de",
            )
            
            environ["TIMEOUT"] = "300"
            storage_id = import_storage["id"]
            print(datetime.datetime.now())
            # this function waits till storage is synchronized
            # TODO check closer what this does, docs imply the stream data from minio, but logs say something about copying
            # if data is just copied to a PVC then we dont need minio buckets for the images we can copy those from repl directly
            project.sync_import_storage(import_storage["type"], storage_id)

            # FIXME that needs to be done to bottom and top, also it should add the project id instead of the name
            #insert_statement = f"""
            #UPDATE robot_logs SET labelstudio_project = '{bucketname}' WHERE log_path = '{logpath}';
            #"""
            #cur.execute(insert_statement)
            #conn.commit()


if __name__ == "__main__":
    """
    """
    data_top = get_logs_with_top_images()
    data_bottom = get_logs_with_bottom_images()

    import_labelstudio(data_top, "#D55C9D")
    import_labelstudio(data_bottom, "#51AAFD")
