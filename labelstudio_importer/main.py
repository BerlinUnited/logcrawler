"""
    Labelstudio importer
"""
import sys
from pathlib import Path
from label_studio_sdk import Client
from minio import Minio
import random
import string

LABEL_STUDIO_URL = 'https://ls.berlinunited-cloud.de/'
API_KEY = '6cb437fb6daf7deb1694670a6f00120112535687'
label_config_bb='''
    <View>
        <Image name="image" value="$image"/>
        <RectangleLabels name="label" toName="image">
        <Label value="ball" background="#9eaeff"/><Label value="nao" background="#D4380D"/><Label value="penalty_mark" background="#e109da"/></RectangleLabels>
    </View>
    '''

def create_project_if_not_exists(project_name, bucket_name):
    ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
    ls.check_connection()

    existing_projects = [a.title for a in ls.list_projects()]
    if project_name in existing_projects:
        print("project already exists")
    else:
        project = ls.start_project(title=project_name,label_config=label_config_bb)

        project.connect_s3_import_storage(bucket=bucket_name, title=project_name, aws_access_key_id="naoth", aws_secret_access_key="HAkPYLnAvydQA", s3_endpoint="https://minio.berlinunited-cloud.de")


def create_bucket_from_logfile(data_folder):
    """
    TODO: rename funtion
    TODO: better secrets handling
    """
    mclient = Minio("minio.berlinunited-cloud.de",
        access_key="naoth",
        secret_key="HAkPYLnAvydQA",
    )

    # TODO handle the case that the name already exist (should only happen by accident)
    bucket_name= ''.join(random.choices(string.ascii_lowercase, k=22))

    # Make the bucket
    mclient.make_bucket(bucket_name)
    print("Created bucket", bucket_name)

    print(f"Upload files in {data_folder}")
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

    return bucket_name



if __name__ == "__main__":
    # TODO use argparse here
    #log_folder = sys.argv[1]
    log_folder= "/mnt/repl/2023-07-04_RC23/2023-07-08_10-30-00_HULKs_vs_Berlin_United_half1-E/extracted/2_24_Nao0011_230708-0843"

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
    create_project_if_not_exists("RC23-Hulks-half1-nao24-top", bucket_name)