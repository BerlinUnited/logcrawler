"""
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
from minio.commonconfig import Tags, SnowballObject
from pathlib import Path
import shutil

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

def handle_bucket(data, overwrite, debug=False):
    # TODO: find better function name
    # TODO make sure we always get the same order (comes in handy during debugging)
    for logpath, bucketname in data:
        print(logpath)
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
        else:
            tags = Tags.new_bucket_tags()
            tags["log path"] = logpath
            mclient.set_bucket_tags(patch_bucket_name, tags)
            if overwrite:
                # delete every object in this bucket
                objects_to_delete = mclient.list_objects(patch_bucket_name, recursive=True)
                for obj in objects_to_delete:
                    mclient.remove_object(patch_bucket_name, obj.object_name)
            
            # TODO set naoth develop version as tag here
        
        #TODO add an option for deleting bucket data and replacing it - maybe based on develop versions?

        evaluator = PatchExecutor()
        objects = mclient.list_objects(bucketname)
        object_list = []
        # iterate over bucket data (assumes that there are only images and nothing else in the bucket)
        for count, obj in enumerate(objects):
            if count >= 3:
                break
            print(obj.object_name)
            # Download an image from minio image bucket 
            # FIXME save it in a tmp folder instead of current working directory
            mclient.fget_object(bucketname, obj.object_name, obj.object_name)

            with cppyy.ll.signals_as_exception():  # this could go into the other file
                frame = evaluator.convert_image_to_frame(obj.object_name)
                evaluator.set_current_frame(frame)
                evaluator.sim.executeFrame()
                # HACK it will be the same folder for each frame
                folder = evaluator.export_patches(frame)
                
                for file in folder.iterdir():
                    # check if it a file
                    if file.is_file():
                        print(f"file: {file.name}")
                        # we will create a snowballobject for each patch file this is done because uploading each patch directly 
                        # results in overloading the server. Minio offers a bulk upload of a list of snowballobjects
                        so = SnowballObject(str(file.name), filename=str(file))
                        object_list.append(so)

                if debug:
                    # FIXME not really implemented yet
                    # TODO rewrite this to return the image
                    return evaluator.export_debug_images(frame)                
            # delete the full size image
            Path(obj.object_name).unlink()

        
        print("uploading snowball object")
        mclient.upload_snowball_objects(bucket_name=patch_bucket_name, object_list=object_list)
        
        # delete the folder with the patches
        if Path(folder).exists():
            shutil.rmtree(folder)


if __name__ == "__main__":
    # TODO use argparse for overwrite flag
    overwrite = True    

    data_top = get_logs_with_top_images()
    data_bottom = get_logs_with_bottom_images()

    handle_bucket(data_top, overwrite)
    handle_bucket(data_bottom, overwrite)