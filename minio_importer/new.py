import psycopg2
import psycopg2.pool
from os import environ
from pathlib import Path
from minio import Minio
from minio.commonconfig import Tags
from tqdm import tqdm
import random
import string

# FIXME make this auto detect if its running inside the cluster or not
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
    "password": environ.get('DB_PASS')
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

def get_top_data():
    select_statement = f"""
    SELECT log_path, bucket_top FROM robot_logs WHERE extract_status = true 
    """
    cursor.execute(select_statement)
    rtn_val = cursor.fetchall()
    logs = [x for x in rtn_val]

    return logs

def find_extracted_image_paths(log_folder: str):
    root_path = Path(environ.get("LOG_ROOT"))
    log_path_w_prefix = root_path / Path(log_folder)
    if Path(log_path_w_prefix).is_file():
        print("\tdetected experiment log")
        actual_log_folder = root_path / Path(log_folder).parent
        extracted_folder = (
            Path(actual_log_folder)
            / Path("extracted")
            / Path(log_path_w_prefix).stem
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
    """
    TODO set up argparser here, if no argument set get all logs from postgres
    """
    root_path = Path(environ.get("LOG_ROOT"))
    bottom_data = get_bottom_data()
    for log_path, bucket_name in sorted(bottom_data):
        print(log_path)

        if not bucket_name:
            bucket_name = generate_unique_name()
            print(f"\tcreated new bucket {bucket_name}")
            # TODO add it to postgres here
            
            #print(f"\t{log_path}")
            # TODO create bucket here
            #mclient.make_bucket(bucket_name)    
            #tags = Tags.new_bucket_tags()
            #tags["data path"] = str(log_path) # set tag to annotate the bucket with the name of the source image folder # FIXME make sure it is set in a common format (wo prefix, log vs extracted folder)
            #mclient.set_bucket_tags(bucket_name, tags)

        else:  # FIXME this should not be in an else instead this should run always no matter if the bucket existed a long time or was just created
            # TODO upload to minio and check each image if it is already uploaded
            # FIXME: make sure we dont have any stale buckets that are not used
            print(f"\tuploading to bucket {bucket_name}")
            data_folder_top, data_folder_bottom = find_extracted_image_paths(log_path)
            minio_files = [mobject.object_name for mobject in mclient.list_objects(bucket_name)]
            local_files = Path(data_folder_bottom).glob("*")
            for file in tqdm(local_files):
                if file.name in minio_files:
                    #print(file.name)
                    pass
                else:
                    print("TODO do the upload here")
                    quit()
    #########################################
    top_data = get_top_data()
    for log_path, bucket_name in sorted(top_data):
        print(log_path)

        if not bucket_name:
            bucket_name = generate_unique_name()
            print(f"\tcreated new bucket {bucket_name}")
            # TODO add it to postgres here
            
            #print(f"\t{log_path}")
            # TODO create bucket here
            #mclient.make_bucket(bucket_name)    
            #tags = Tags.new_bucket_tags()
            #tags["data path"] = str(log_path) # set tag to annotate the bucket with the name of the source image folder # FIXME make sure it is set in a common format (wo prefix, log vs extracted folder)
            #mclient.set_bucket_tags(bucket_name, tags)

        else:  # FIXME this should not be in an else instead this should run always no matter if the bucket existed a long time or was just created
            # TODO upload to minio and check each image if it is already uploaded
            # FIXME: make sure we dont have any stale buckets that are not used
            print(f"\tuploading to bucket {bucket_name}")
            data_folder_top, data_folder_bottom = find_extracted_image_paths(log_path)
            minio_files = [mobject.object_name for mobject in mclient.list_objects(bucket_name)]
            local_files = Path(data_folder_top).glob("*")
            for file in tqdm(local_files):
                if file.name in minio_files:
                    #print(file.name)
                    pass
                else:
                    print("TODO do the upload here")
                    quit()
    quit()  
    #print()
    #print()
    # 2024-04-17_GO24/2024-04-18_18-00-00_Berlin United_vs_HTWK_half2/game_logs/3_22_Nao0004_240418-1653 pilblbbuppbzsfwolyxovs
    extracted_folder = "/mnt/q/logs/2024-04-17_GO24/2024-04-18_18-00-00_Berlin United_vs_HTWK_half2/extracted/3_22_Nao0004_240418-1653/log_bottom"
    # minio
    minio_files = [mobject.object_name for mobject in mclient.list_objects("pilblbbuppbzsfwolyxovs")]
    local_files = Path(extracted_folder).glob("*")
    for file in tqdm(local_files):
        if file.name in minio_files:
            #print(file.name)
            pass
        else:
            print("TODO do the upload here")

    #for mobject in minio_files:
    #    print(mobject.object_name)