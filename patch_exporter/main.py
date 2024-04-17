"""
ARRRRGH: https://github.com/wlav/cppyy/issues/176

FIXME: ignore cancelled tasks (we have logs with broken images)
Run the patch export v1
    - get logs with image data from postgres
    - get the bucket
    - create new bucket with name: old_bucketname_patches
    - download image
        - run patch extraction on the image (patches are named: image_name_patch{number}
        - upload patches to new bucket
        - delete image and patches to conserve space

Run the patch export v2
    - get logs with image data from postgres
    - get labelstudio project
    - get the bucket corresponding to the project
    - create new bucket with name: old_bucketname_patches
    - for each task in project:
        - download image
        - run patch extraction on the image it should return the pixel locations of the patch and export the image to png (patches are named: image_name_patch{number})
        - for each patch:
            - calculate the overlap with each annotation region
            - if overlap is high enough put the image in a different folder (maybe)
        - upload patches to new bucket
        - delete image and patches to conserve space
"""
import psycopg2
import cppyy
from minio import Minio
from minio.commonconfig import Tags
from pathlib import Path
import shutil
import time
from tqdm import tqdm
from os import environ
from label_studio_sdk import Client
from PatchExecutor import PatchExecutor
import tempfile
from helper import Rectangle, Point2D

params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get('DB_PASS')
}
conn = psycopg2.connect(**params)
cur = conn.cursor()

mclient = Minio("minio.berlinunited-cloud.de",
    access_key="naoth",
    secret_key=environ.get("MINIO_PASS"),
)

LABEL_STUDIO_URL = 'https://ls.berlinunited-cloud.de/'
API_KEY = '6cb437fb6daf7deb1694670a6f00120112535687'

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()

evaluator = PatchExecutor()

def get_buckets_with_top_images():
    select_statement = f"""
    SELECT log_path,bucket_top FROM robot_logs WHERE bucket_top IS NOT NULL
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]
    return logs


def get_buckets_with_bottom_images():
    select_statement = f"""
    SELECT log_path, bucket_bottom FROM robot_logs WHERE bucket_bottom IS NOT NULL
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]
    return logs

def get_ls_project_from_name(project_name: str):
    """
    In our database the project name is the same as the bucket name. For interacting with the labelstudio API we need the project ID
    """
    project_list = ls.list_projects()
    for project in project_list:
        if project.title == project_name:
            return project

def create_patch_bucket(logpath, bucketname, db_field):
    patch_bucket_name = bucketname + "-patches"
    if not mclient.bucket_exists(patch_bucket_name):
        mclient.make_bucket(patch_bucket_name)
        print("\tcreated bucket", patch_bucket_name)
        # annotate the bucket with the name of the log
        
        tags = Tags.new_bucket_tags()
        tags["log path"] = logpath
        mclient.set_bucket_tags(patch_bucket_name, tags)
        # TODO set naoth develop version as tag 
        exists = False
        
    else:
        print(f"\tbucket {patch_bucket_name} already exists")
        tags = Tags.new_bucket_tags()
        tags["log path"] = logpath
        mclient.set_bucket_tags(patch_bucket_name, tags)
        # TODO set naoth develop version as tag here
        exists = True
    
        
    # add bucketname to postgres
    insert_statement = f"""
    UPDATE robot_logs SET {db_field} = '{patch_bucket_name}' WHERE log_path = '{logpath}';
    """
    cur.execute(insert_statement)
    conn.commit()
    #TODO add an option for deleting bucket data and replacing it - maybe based on develop versions?
    return patch_bucket_name, exists

def handle_bucket(data, db_field, debug):
    # TODO: find better function name
    # TODO make sure we always get the same order (comes in handy during debugging)
    # TODO put data in same bucket (maybe)
    for logpath, bucketname in sorted(data):
        print(logpath)

        # get project matching the bucket here HACK assumes that ls project name is the same as bucket name
        # probably we can get the bucket name directly from the projects somehow. -> would be more future prove
        ls_project = get_ls_project_from_name(bucketname)
        
        # Create the bucket for the patches
        patch_bucket_name, exists = create_patch_bucket(logpath, bucketname, db_field)
        if exists:
            continue

        # TODO setup temp dir for downloaded images
        tmp_download_folder = tempfile.TemporaryDirectory()

        print('\tcreated temporary directory', tmp_download_folder)
        # get list of tasks
        task_ids = ls_project.get_labeled_tasks_ids()
        for task in tqdm(task_ids):
            image_file_name = ls_project.get_task(task)["storage_filename"]
            output_file = Path(tmp_download_folder.name) / image_file_name
            # download the image from minio
            mclient.fget_object(bucketname, image_file_name, str(output_file))
            # TODO get meta information from png header

            # TODO get the annotation
            ball_list = list()
            annotations = ls_project.get_task(task)["annotations"]
            for anno in annotations:
                results = anno["result"]
                # print(anno)
                for result in results:
                    # x,y,width,height are all percentages within [0,100]
                    x, y, width, height = result["value"]["x"], result["value"]["y"], result["value"]["width"], result["value"]["height"]
                    img_width = result['original_width']
                    img_height = result['original_height']
                    actual_label = result["value"]["rectanglelabels"][0]
                    if actual_label == "ball":
                        x_px = x / 100 * img_width
                        y_px = y / 100 * img_height
                        width_px = width / 100 * img_width
                        height_px = height / 100 * img_height
                        ball_list.append(Rectangle(Point2D(x_px, y_px), Point2D(x_px + width_px, y_px + height_px)))

                    #label_id = label_dict[actual_label]
            
            # TODO get all the bboxes in the correct format in a list
            
            output_patch_folder = Path(tmp_download_folder.name) / "patches"
            output_patch_folder.mkdir(exist_ok=True)
            # get patches
            with cppyy.ll.signals_as_exception():  # this could go into the other file
                frame = evaluator.convert_image_to_frame(str(output_file), ball_list)
                evaluator.set_current_frame(frame)
                evaluator.sim.executeFrame()
                
                evaluator.export_patches(frame, output_patch_folder, bucketname)

        print("\tcreating archive of all the patches")
        # creates patches.zip in the current folder
        shutil.make_archive("patches", 'zip', str(output_patch_folder))
        tmp_download_folder.cleanup()

        print(f"uploading object to {patch_bucket_name}")
        mclient.fput_object(
            patch_bucket_name,
            "patches.zip",
            "patches.zip",
        )


def delete_data(data):
    # FIXME move to minio tools
    for logpath, bucketname in data:
        print(logpath)
        patch_bucket_name = bucketname + "-patches"
        if overwrite and mclient.bucket_exists(patch_bucket_name):
            # delete every object in this bucket
            print(f"\tdeleting files in {patch_bucket_name}")
            objects_to_delete = mclient.list_objects(patch_bucket_name, recursive=True)
            for obj in objects_to_delete:
                print(f"\t\tremoving {obj.object_name}")
                mclient.remove_object(patch_bucket_name, obj.object_name)

if __name__ == "__main__":
    # TODO use argparse for overwrite flag
    overwrite = False    

    data_top = get_buckets_with_top_images()
    data_bottom = get_buckets_with_bottom_images()
    
    if overwrite:
        delete_data(data_top)
        delete_data(data_bottom)
        time.sleep(15)

    handle_bucket(data_top, db_field="bucket_top_patches", debug=False)
    handle_bucket(data_bottom, db_field="bucket_bottom_patches", debug=False)