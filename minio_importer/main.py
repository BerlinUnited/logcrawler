"""
    TODO: I could put all the images in a folder inside the bucket, this would leave room for also putting sound and other data in the bucket
"""
from os import environ
import psycopg2
from pathlib import Path
from minio import Minio
from minio.commonconfig import Tags
import random
import string
import json

mclient = Minio(
    "minio.berlinunited-cloud.de",
    access_key="naoth",
    secret_key=environ.get("MINIO_PASS"),
)

# Hack we set a global policy on all buckets, technically we only need to set it once
# The only thing this prevents is deletion of buckets when the last element was deleted
minio_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": ["s3:ForceDeleteBucket", "s3:DeleteBucket"],
            "Resource": "arn:aws:s3:::*",
        }
    ],
    }

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
    SELECT log_path FROM robot_logs WHERE extract_status = true 
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x[0] for x in rtn_val]
    return logs


def generate_unique_name():
    while True:
        name = "".join(random.choices(string.ascii_lowercase, k=22))
        if not mclient.bucket_exists(name):
            return name


def upload_to_minio(data_folder):
    # TODO check if a name in db exist already and use that 
    bucket_name = generate_unique_name()

    # Make the bucket
    # TODO maybe add a try here so that we can remove the bucket if something goes wrong
    mclient.make_bucket(bucket_name)
    # set tag to annotate the bucket with the name of the source image folder
    tags = Tags.new_bucket_tags()
    tags["data path"] = str(data_folder)
    mclient.set_bucket_tags(bucket_name, tags)
    mclient.set_bucket_policy(bucket_name, json.dumps(minio_policy))
    
    print("Created bucket", bucket_name)

    print(f"Upload files in {data_folder}")
    files = Path(data_folder).glob("*")
    for file in files:
        print(f"{file}", end="\r", flush=True)
        source_file = file
        destination_file = Path(file).name
        mclient.fput_object(
            bucket_name,
            destination_file,
            source_file,
        )
    return bucket_name


if __name__ == "__main__":
    """
    TODO set up argparser here, if no argument set get all logs from postgres
    FIXME: this cant be executed twice yet
    """
    root_path = Path(environ.get("LOG_ROOT"))
    log_list = get_logs()

    for log_folder in log_list:
        actual_log_folder = root_path / Path(log_folder)
        combined_log = root_path / Path(actual_log_folder) / "combined.log"
        game_log = root_path / Path(actual_log_folder) / "game.log"

        extracted_folder = (
            Path(actual_log_folder).parent.parent
            / Path("extracted")
            / Path(actual_log_folder).name
        )
        data_folder_top = extracted_folder / Path("log_top")
        data_folder_bottom = extracted_folder / Path("log_bottom")

        # check if bucket for top data exists (FIXME make this code cooler)
        # TODO can we have a policy against bucket deletion?
        select_statement = f"""
        SELECT bucket_top FROM robot_logs WHERE log_path = '{log_folder}' 
        """
        cur.execute(select_statement)
        rtn_val = cur.fetchall()[0][0]
        if rtn_val is not None:
            # TODO this must be handled better for example what if minio goes down and looses all the data, I need to recreate it the same way. this way I can also use the labelstudio backup
            print("bucket already exists")
        else:
            bucket_name_top = upload_to_minio(data_folder_top)
            insert_statement = f"""
            UPDATE robot_logs SET bucket_top = '{bucket_name_top}' WHERE log_path = '{log_folder}';
            """
            cur.execute(insert_statement)
            conn.commit()

        # check if bucket for bottom data exists (FIXME make this code cooler)
        select_statement = f"""
        SELECT bucket_bottom FROM robot_logs WHERE log_path = '{log_folder}' 
        """
        cur.execute(select_statement)
        rtn_val = cur.fetchall()[0][0]
        if rtn_val is not None:
            print("bucket already exists")
        else:
            bucket_name_bottom = upload_to_minio(data_folder_bottom)
            insert_statement = f"""
            UPDATE robot_logs SET bucket_bottom = '{bucket_name_bottom}' WHERE log_path = '{log_folder}';
            """
            cur.execute(insert_statement)
            conn.commit()
