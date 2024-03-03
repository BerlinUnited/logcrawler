"""
    Labelstudio importer
"""
import sys
from pathlib import Path
from label_studio_sdk import Client
from minio import Minio

def create_bucket_from_logfile(bucket_name, data_folder):
    """
    bucket name must be unique: so calculate it from event, game and log foldername + top /bottom
    """
    mclient = Minio("minio.berlinunited-cloud.de",
        access_key="naoth",
        secret_key="HAkPYLnAvydQA",
    )
    # Make the bucket if it doesn't exist.
    found = mclient.bucket_exists(bucket_name)
    if not found:
        mclient.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    files = Path(data_folder).glob('*')
    for file in files:
        print(file)
        source_file = file
        destination_file = Path(file).name
        mclient.fput_object(
            bucket_name, destination_file, source_file,
        )
        print(
            source_file, "successfully uploaded as object",
            destination_file, "to bucket", bucket_name,
        )

#


if __name__ == "__main__":
    # TODO use argparse here
    #log_folder = sys.argv[1]
    log_folder= "/mnt/q/2023-07-04_RC23/2023-07-08_10-30-00_HULKs_vs_Berlin_United_half1-E/extracted/1_13_Nao0038_230708-0843"

    log_name = Path(log_folder).name
    game_name = Path(log_folder).parent.parent.name
    event_name = Path(log_folder).parent.parent.parent.name

    bucket_name_bottom = event_name + "#" + game_name + "#" + log_name + "#bottom"
    bucket_name_top = event_name + "#" + game_name + "#" + log_name + "#top"

    bottom_data = Path(log_folder) / Path("extracted") / Path("combined_bottom")
    top_data = Path(log_folder) / Path("extracted") / Path("combined_top")
    # TODO play around with zip files and minio
    create_bucket_from_logfile(bucket_name_bottom, bottom_data)
    create_bucket_from_logfile(bucket_name_top, top_data)

    