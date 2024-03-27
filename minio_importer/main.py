from os import environ
import psycopg2
from pathlib import Path
from minio import Minio
from minio.commonconfig import Tags
import random
import string

mclient = Minio(
    "minio.berlinunited-cloud.de",
    access_key="naoth",
    secret_key="HAkPYLnAvydQA",
)

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
    bucket_name = generate_unique_name()

    # Make the bucket
    # TODO maybe add a try here so that we can remove the bucket if something goes wrong
    mclient.make_bucket(bucket_name)
    # set tag to annotate the bucket with the name of the source image folder
    tags = Tags.new_bucket_tags()
    tags["data path"] = str(data_folder)
    mclient.set_bucket_tags(bucket_name, tags)
    
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
    # FIXME '/mnt/q/' is specific to my windows setup - make sure it works on other machines as well
    root_path = (
        environ.get("LOG_ROOT") or "/mnt/q/"
    )  # use or with environment variable to make sure it works in k8s as well
    root_path = Path(root_path)
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
        select_statement = f"""
        SELECT bucket_top FROM robot_logs WHERE log_path = '{log_folder}' 
        """
        cur.execute(select_statement)
        rtn_val = cur.fetchall()[0][0]
        if rtn_val is not None:
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
