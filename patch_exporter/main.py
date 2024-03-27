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

from PatchExecutor import PatchExecutor

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
    secret_key="HAkPYLnAvydQA",
)

evaluator = PatchExecutor()

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

def handle_bucket(data, db_field, debug):
    # TODO: find better function name
    # TODO make sure we always get the same order (comes in handy during debugging)
    for logpath, bucketname in data:
        print(logpath)
        patch_bucket_name = bucketname + "-patches"
        
        # Make the patch_bucket_name
        if not mclient.bucket_exists(patch_bucket_name):
            mclient.make_bucket(patch_bucket_name)
            print("\tcreated bucket", patch_bucket_name)
            # annotate the bucket with the name of the log
            
            tags = Tags.new_bucket_tags()
            tags["log path"] = logpath
            mclient.set_bucket_tags(patch_bucket_name, tags)
            # TODO set naoth develop version as tag here
            
        else:
            print(f"\tbucket {patch_bucket_name} already exists")
            tags = Tags.new_bucket_tags()
            tags["log path"] = logpath
            mclient.set_bucket_tags(patch_bucket_name, tags)
            # TODO set naoth develop version as tag here
            
        # add bucketname to postgres
        insert_statement = f"""
        UPDATE robot_logs SET {db_field} = '{patch_bucket_name}' WHERE log_path = '{logpath}';
        """
        cur.execute(insert_statement)
        conn.commit()
        #TODO add an option for deleting bucket data and replacing it - maybe based on develop versions?

        
        objects = mclient.list_objects(bucketname)

        # iterate over bucket data (assumes that there are only images and nothing else in the bucket)
        for count, obj in enumerate(objects):
            #print(obj.object_name)
            # Download an image from minio image bucket 
            # FIXME save it in a tmp folder instead of current working directory
            mclient.fget_object(bucketname, obj.object_name, obj.object_name)

            with cppyy.ll.signals_as_exception():  # this could go into the other file
                frame = evaluator.convert_image_to_frame(obj.object_name)
                evaluator.set_current_frame(frame)
                evaluator.sim.executeFrame()
                # HACK it will be the same folder for each frame
                folder = evaluator.export_patches(frame)
                
                if debug:
                    # FIXME not really implemented yet
                    # TODO rewrite this to return the image
                    return evaluator.export_debug_images(frame)                
            # delete the full size image
            Path(obj.object_name).unlink()

        shutil.make_archive("patches", 'zip', folder)
        print(f"uploading object to {patch_bucket_name}")
        mclient.fput_object(
            patch_bucket_name,
            "patches.zip",
            "patches.zip",
        )
        
        # delete the folder with the patches
        if Path(folder).exists():
            shutil.rmtree(folder)
        if Path("patches.zip").exists():
            Path("patches.zip").unlink()

def delete_data(data):
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
    overwrite = True    
    
        
    data_top = get_logs_with_top_images()
    data_bottom = get_logs_with_bottom_images()
    
    if overwrite:
        delete_data(data_top)
        delete_data(data_bottom)
        time.sleep(15)

    handle_bucket(data_top, db_field="bucket_top_patches", debug=False)
    handle_bucket(data_bottom, db_field="bucket_bottom_patches", debug=False)