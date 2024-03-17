"""
    Run the patch export v1


- get logs with image data from postgres
- get the bucket
- create new bucket with name: old_bucketname_patches
- download image
    - run patch extraction on the image (patches are named: image_name_patch{number}=
    - upload patches to new bucket
    - delete image and patches to conserve space
"""


"""
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

from PatchExecutor import PatchExecutor

params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": "fsdjhwzuertuqg",
}
conn = psycopg2.connect(**params)
cur = conn.cursor()

mclient = Minio("minio.berlinunited-cloud.de",
    access_key="naoth",
    secret_key="HAkPYLnAvydQA",
)

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

def handle_bucket(data):
    # TODO: find better function name
    for logpath, bucketname in data:
        print(bucketname)
        patch_bucket_name = bucketname + "-patches"

        # TODO add the new bucket to new column in postgres

        # Make the patch_bucket_name
        if not mclient.bucket_exists(patch_bucket_name):
            mclient.make_bucket(patch_bucket_name)
            # notate the bucket with the name of the log
            print("Created bucket", patch_bucket_name)
            tags = Tags.new_bucket_tags()
            tags["log path"] = logpath
            mclient.set_bucket_tags(patch_bucket_name, tags)
            # TODO set naoth develop version as tag here
        
        #TODO add an option for deleting bucket data and replacing it - maybe based on develop versions?
            
        # iterate over bucket data (assumes that there are only images and nothing else in the bucket)
            
        evaluator = PatchExecutor()
        objects = mclient.list_objects(bucketname)
        for obj in objects:
            print(obj.object_name)
            # TODO save it in a tmp folder
            mclient.fget_object(bucketname, obj.object_name, obj.object_name)

            # TODO run patch extractor here
            # TODO maybe have this constructor outside of the loop for speedup
            #evaluator = PatchExecutor()
            with cppyy.ll.signals_as_exception():  # this could go into the other file
                folder = evaluator.execute_frame(obj.object_name) # FIXME the folder needs to be cleaned also the bucket should only contain the images and not the full path
                for file in folder.iterdir():
                    print(f"file: {file}")
                    # check if it a file
                    if file.is_file():
                        result = mclient.fput_object(patch_bucket_name, str(file), str(file))
        quit()


if __name__ == "__main__":
    data_top = get_logs_with_top_images()
    data_bottom = get_logs_with_bottom_images()

    handle_bucket(data_top)
    handle_bucket(data_bottom)