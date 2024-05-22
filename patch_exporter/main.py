"""
 Pretty ulgy implementation for patch detection. Has a ton of problems!!!
"""

import argparse
import shutil
import tempfile
from os import environ
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import cppyy
import psycopg2
from helper import BoundingBox, Point2D
from label_studio_sdk import Client
from minio import Minio
from minio.commonconfig import Tags
from PatchExecutor import PatchExecutor
from tqdm import tqdm

params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get("DB_PASS"),
}
conn = psycopg2.connect(**params)
cur = conn.cursor()

mclient = Minio(
    "minio.berlin-united.com",
    access_key="naoth",
    secret_key=environ.get("MINIO_PASS"),
)

LABEL_STUDIO_URL = "https://ls.berlin-united.com/"
API_KEY = "6cb437fb6daf7deb1694670a6f00120112535687"

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()

evaluator = PatchExecutor()


def get_buckets_with_top_images(
    event_names: Optional[List[str]] = None,
    ls_project_ids: Optional[List[Union[str, int]]] = None,
    validated_only: bool = True,
) -> Tuple[str, str, str]:

    select_statement = f"""        
    SELECT log_path, bucket_top, ls_project_top
    FROM robot_logs
    WHERE bucket_top IS NOT NULL
    AND ls_project_top IS NOT NULL
    """

    if event_names:
        event_names_str = ", ".join([f"'{x}'" for x in event_names])
        select_statement += f"AND event_name IN ({event_names_str})\n"

    if ls_project_ids:
        project_ids_str = ", ".join([f"'{x}'" for x in ls_project_ids])
        select_statement += f"AND ls_project_top IN ({project_ids_str})\n"

    if validated_only:
        select_statement += "AND top_validated = true\n"

    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]
    return logs


def get_buckets_with_bottom_images(
    event_names: Optional[List[str]] = None,
    ls_project_ids: Optional[List[Union[str, int]]] = None,
    validated_only: bool = True,
) -> Tuple[str, str, str]:

    select_statement = f"""        
    SELECT log_path, bucket_bottom, ls_project_bottom
    FROM robot_logs
    WHERE bucket_bottom IS NOT NULL
    AND ls_project_bottom IS NOT NULL
    """

    if event_names:
        event_names_str = ", ".join([f"'{x}'" for x in event_names])
        select_statement += f"AND event_name IN ({event_names_str})\n"

    if ls_project_ids:
        project_ids_str = ", ".join([f"'{x}'" for x in ls_project_ids])
        select_statement += f"AND ls_project_bottom IN ({project_ids_str})\n"

    if validated_only:
        select_statement += "AND bottom_validated = true\n"

    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x for x in rtn_val]
    return logs


def create_patch_bucket(logpath: str, bucketname, db_field: str) -> Tuple[str, bool]:
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
    # TODO add an option for deleting bucket data and replacing it - maybe based on develop versions?
    return patch_bucket_name, exists


def gt_ball_bounding_boxes_from_labelstudio_task(
    task: Dict,
) -> Tuple[List[BoundingBox], List[BoundingBox], List[BoundingBox]]:
    ball_list = list()
    robot_list = list()
    penalty_mark_list = list()

    for annotation in task["annotations"]:
        for result in annotation["result"]:
            # x,y,width,height are all percentages within [0,100]
            x, y, width, height = (
                result["value"]["x"],
                result["value"]["y"],
                result["value"]["width"],
                result["value"]["height"],
            )
            img_width = result["original_width"]
            img_height = result["original_height"]
            actual_label = result["value"]["rectanglelabels"][0]

            if actual_label in ("ball", "nao", "penalty_mark"):
                x_px = x / 100 * img_width
                y_px = y / 100 * img_height
                width_px = width / 100 * img_width
                height_px = height / 100 * img_height

                top_left = Point2D(x_px, y_px)
                bottom_right = Point2D(x_px + width_px, y_px + height_px)
                bounding_box = BoundingBox(top_left, bottom_right)

                if actual_label == "ball":
                    ball_list.append(bounding_box)
                elif actual_label == "nao":
                    robot_list.append(bounding_box)
                elif actual_label == "penalty_mark":
                    penalty_mark_list.append(bounding_box)

    return ball_list, robot_list, penalty_mark_list


def upload_patches_zip_to_bucket(
    patch_bucket_name: str, output_patch_folder: Union[str, Path]
):
    shutil.make_archive("patches", "zip", str(output_patch_folder))

    # upload patches.zip to the patch bucket
    print(f"uploading object to {patch_bucket_name}")

    mclient.fput_object(
        patch_bucket_name,
        "patches.zip",
        "patches.zip",
    )


def create_patches_from_annotations(
    logpath: str,
    bucketname: str,
    ls_project_id: Union[int, str],
    db_field: str,
    overwrite: bool = False,
    debug: bool = False,
):
    # TODO put data in same bucket (maybe)
    # TODO get meta information from png header
    # TODO get all the bboxes in the correct format in a list

    ls_project = ls.get_project(id=ls_project_id)
    labeled_tasks = ls_project.get_labeled_tasks()

    if not labeled_tasks:
        print("\tNo labeled tasks found for this project, skipping...")
        return

    #Create the bucket for the patches
    patch_bucket_name, patch_bucket_exists = create_patch_bucket(
        logpath, bucketname, db_field
    )

    if patch_bucket_exists and not overwrite:
        print("\tBucket already exists and overwrite is not set, skipping...")
        return

    tmp_download_folder = tempfile.TemporaryDirectory()
    output_patch_folder = Path(tmp_download_folder.name) / "patches"
    output_patch_folder.mkdir(exist_ok=True, parents=True)

    print(f"\t Created temporary directory {tmp_download_folder}")

    for task in tqdm(labeled_tasks):
        image_file_name = task["storage_filename"]
        output_file = Path(tmp_download_folder.name) / image_file_name

        # download the image from minio
        mclient.fget_object(bucketname, image_file_name, str(output_file))

        # get the bounding boxes from the task
        ball_list, robot_list, penalty_list = (
            gt_ball_bounding_boxes_from_labelstudio_task(task)
        )

        # export patches with naoth cpp code
        with cppyy.ll.signals_as_exception():  # this could go into the other file
            frame = evaluator.convert_image_to_frame(
                str(output_file),
                gt_balls=ball_list,
                gt_robots=robot_list,
                gt_penalties=penalty_list,
            )
            evaluator.set_current_frame(frame)
            evaluator.sim.executeFrame()

            evaluator.export_patches(
                frame,
                output_patch_folder,
                bucketname,
                debug=debug,
            )

            if debug:
                evaluator.export_debug_images(frame)

    # upload the patches to the bucket
    upload_patches_zip_to_bucket(patch_bucket_name, output_patch_folder)

    # cleanup
    tmp_download_folder.cleanup()


if __name__ == "__main__":
    # TODO make it possible to export specific buckets

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--project",
        nargs="+",
        required=False,
        type=int,
        help="Labelstudio project ids separated by a space",
    )
    parser.add_argument(
        "-e",
        "--event",
        nargs="+",
        required=False,
        type=str,
        help="Event names separated by a space",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Set flag to overwrite existing patch data",
    )
    parser.add_argument(
        "--unvalidated",
        action="store_true",
        default=False,
        help="Set flag to export unvalidated patches, default is to only export validated LabelStudio projects",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Set flag to enable debug mode",
    )

    args = parser.parse_args()
    events = args.event
    projects = args.project
    overwrite = args.overwrite
    validated_only = not args.unvalidated
    debug = args.debug

    # get the buckets with top and bottom images,
    # use LabelStudio project IDs as a filter if they were provided
    data_top = get_buckets_with_top_images(
        event_names=events, ls_project_ids=projects, validated_only=validated_only
    )
    data_bottom = get_buckets_with_bottom_images(
        event_names=events, ls_project_ids=projects, validated_only=validated_only
    )

    # TODO: Move all top/bottom logic into one function
    # add the db_field info to the data
    data_top = [
        (logpath, bucketname, ls_project_id, "bucket_top_patches")
        for logpath, bucketname, ls_project_id in data_top
    ]
    data_bottom = [
        (logpath, bucketname, ls_project_id, "bucket_bottom_patches")
        for logpath, bucketname, ls_project_id in data_bottom
    ]

    data_combined = sorted(data_top + data_bottom, reverse=True)
    print(f"Found {len(data_combined)} buckets to process")

    # for each bucket, loop over all annotated images in LabelStudio and create patches
    # with the naoth cpp code using the annotations as ball ground truth
    for logpath, bucketname, ls_project_id, db_field in data_combined:
        print(f"Creating {db_field} patches for ", end="")
        print(f"Log: {logpath}, Bucket: {bucketname}, LS Project: {ls_project_id}")

        create_patches_from_annotations(
            logpath=logpath,
            bucketname=bucketname,
            ls_project_id=ls_project_id,
            db_field=db_field,
            overwrite=overwrite,
            debug=debug,
        )
