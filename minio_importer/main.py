import argparse
import random
import string
from os import environ
from pathlib import Path

import psycopg2
import psycopg2.pool
from minio import Minio
from minio.commonconfig import Tags
from tqdm import tqdm

# make this auto detect if its running inside the cluster or not
if "KUBERNETES_SERVICE_HOST" in environ:
    postgres_host = "postgres-postgresql.postgres.svc.cluster.local"
    postgres_port = 5432
else:
    postgres_host = "pg.berlinunited-cloud.de"
    postgres_port = 4000

params = {
    "host": postgres_host,
    "port": postgres_port,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get("DB_PASS"),
}

conn = psycopg2.connect(**params)
cursor = conn.cursor()

mclient = Minio(
    "minio.berlinunited-cloud.de",
    access_key="naoth",
    secret_key=environ.get("MINIO_PASS"),
)


def generate_unique_name():
    while True:
        name = "".join(random.choices(string.ascii_lowercase, k=22))
        if not mclient.bucket_exists(name):
            return name


def get_bottom_data():
    select_statement = f"""
    SELECT log_path, bucket_bottom FROM robot_logs WHERE extract_status = true 
    """
    cursor.execute(select_statement)
    rtn_val = cursor.fetchall()
    logs = [x for x in rtn_val]

    return logs


def get_new_bottom_data():
    select_statement = f"""
    SELECT log_path FROM robot_logs WHERE extract_status = true AND bucket_bottom IS NULL
    """
    cursor.execute(select_statement)
    rtn_val = cursor.fetchall()
    logs = [x[0] for x in rtn_val]

    return logs


def get_top_data():
    select_statement = f"""
    SELECT log_path, bucket_top FROM robot_logs WHERE extract_status = true 
    """
    cursor.execute(select_statement)
    rtn_val = cursor.fetchall()
    logs = [x for x in rtn_val]

    return logs


def get_new_top_data():
    select_statement = f"""
    SELECT log_path FROM robot_logs WHERE extract_status = true AND bucket_top IS NULL
    """
    cursor.execute(select_statement)
    rtn_val = cursor.fetchall()
    logs = [x[0] for x in rtn_val]

    return logs


def find_extracted_image_paths(log_folder: str):
    root_path = Path(environ.get("LOG_ROOT"))
    log_path_w_prefix = root_path / Path(log_folder)
    if Path(log_path_w_prefix).is_file():
        print("\tdetected experiment log")
        actual_log_folder = root_path / Path(log_folder).parent
        extracted_folder = (
            Path(actual_log_folder) / Path("extracted") / Path(log_path_w_prefix).stem
        )
        data_folder_top = extracted_folder / Path("log_top")
        data_folder_bottom = extracted_folder / Path("log_bottom")
    else:
        print("\tdetected normal game log")
        actual_log_folder = root_path / Path(log_folder)
        # calculate the location of the folders for the images
        extracted_folder = (
            Path(actual_log_folder).parent.parent
            / Path("extracted")
            / Path(actual_log_folder).name
        )

        data_folder_top = extracted_folder / Path("log_top")
        data_folder_bottom = extracted_folder / Path("log_bottom")

    return data_folder_top, data_folder_bottom


if __name__ == "__main__":
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
    bottom_data = get_bottom_data() if should_check_all else get_new_bottom_data()
    for log_path, bucket_name in sorted(bottom_data, reverse=True):
        print(log_path)

        if not bucket_name:
            bucket_name = generate_unique_name()
            print(f"\tcreated new bucket {bucket_name}")

            mclient.make_bucket(bucket_name)
            tags = Tags.new_bucket_tags()
            tags["data path"] = str(
                log_path
            )  # set tag to annotate the bucket with the name of the source image folder # FIXME make sure it is set in a common format (wo prefix, log vs extracted folder)
            mclient.set_bucket_tags(bucket_name, tags)

        # FIXME: make sure we dont have any stale buckets that are not used
        data_folder_top, data_folder_bottom = find_extracted_image_paths(log_path)
        minio_files = [
            mobject.object_name for mobject in mclient.list_objects(bucket_name)
        ]
        local_files = Path(data_folder_bottom).glob("*")
        for file in tqdm(local_files):
            if file.name in minio_files:
                print(f"\tfile already exists in bucket {bucket_name}, skipping upload")
                pass
            else:
                print(f"\tuploading to bucket {bucket_name}")
                source_file = file
                destination_file = Path(file).name
                mclient.fput_object(
                    bucket_name,
                    destination_file,
                    source_file,
                )
        insert_statement = f"""
        UPDATE robot_logs SET bucket_bottom = '{bucket_name}' WHERE log_path = '{log_path}';
        """
        cursor.execute(insert_statement)
        conn.commit()

    #########################################
    top_data = get_top_data() if should_check_all else get_new_top_data()
    for log_path, bucket_name in sorted(top_data, reverse=True):
        print(log_path)

        if not bucket_name:
            bucket_name = generate_unique_name()
            print(f"\tcreated new bucket {bucket_name}")

            mclient.make_bucket(bucket_name)
            tags = Tags.new_bucket_tags()
            tags["data path"] = str(
                log_path
            )  # set tag to annotate the bucket with the name of the source image folder # FIXME make sure it is set in a common format (wo prefix, log vs extracted folder)
            mclient.set_bucket_tags(bucket_name, tags)

        # FIXME: make sure we dont have any stale buckets that are not used
        print(f"\tuploading to bucket {bucket_name}")
        data_folder_top, data_folder_bottom = find_extracted_image_paths(log_path)
        minio_files = [
            mobject.object_name for mobject in mclient.list_objects(bucket_name)
        ]
        local_files = Path(data_folder_top).glob("*")
        for file in tqdm(local_files):
            if file.name in minio_files:
                # print(file.name)
                pass
            else:
                # print(f"\t\tuploading {file.name}", end="\r", flush=True)
                source_file = file
                destination_file = Path(file).name
                mclient.fput_object(
                    bucket_name,
                    destination_file,
                    source_file,
                )
        insert_statement = f"""
        UPDATE robot_logs SET bucket_top = '{bucket_name}' WHERE log_path = '{log_path}';
        """
        cursor.execute(insert_statement)
        conn.commit()
