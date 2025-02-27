from pathlib import Path
from typing import Generator, List
import os
from time import sleep

from vaapi.client import Vaapi


def scandir_yield_files(directory):
    """Generator that yields file paths in a directory."""
    with os.scandir(directory) as it:
        for entry in it:
            if entry.is_file():
                yield entry.path

def path_generator(directory: str, batch_size: int = 200) -> Generator[List[str], None, None]:
    batch = []
    for path in scandir_yield_files(directory):
        batch.append(path)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

def handle_insertion(individual_extracted_folder, log, camera, image_type):

    print(individual_extracted_folder)
    if not Path(individual_extracted_folder).is_dir():
        return

    if is_done(log.id, camera, image_type):
        return

    # get list of frames  for this log
    frames = client.cognitionframe.list(log=log.id)
    # Create a dictionary mapping frame_number to id
    frame_to_id = {frame.frame_number: frame.id for frame in frames}

    def get_id_by_frame_number(target_frame_number):
        return frame_to_id.get(target_frame_number, None)

    for batch in path_generator(individual_extracted_folder):
        image_ar = [None] * len(batch)
        for idx, file in enumerate(batch):
            # get frame number
            framenumber = int(Path(file).stem)
            url_path = str(file).removeprefix(log_root_path).strip("/")
            
            image_ar[idx] = {
                "frame": get_id_by_frame_number(framenumber),
                "camera": camera,
                "type": image_type,
                "image_url": url_path,
                # HACK we need to provide some default values
                "blurredness_value": None,
                "brightness_value": None,
                "resolution": None,
            }
        try:
            response = client.image.bulk_create(
                data_list=image_ar
            )
        except Exception as e:
            print(f"error inputing the data {log_path}")
            print(e)

        sleep(0.5)
    #sleep(5)

def is_done(robot_data_id, camera, image_type):
    response = client.image.get_image_count(log=robot_data_id, camera=camera, type=image_type)
    db_count = int(response["count"])
    # FIXME use the correct data for check if its done
    response2 = client.log_status.list(log=robot_data_id)
    if len(response2) == 0:
        print("\tno log_status found")
        return False
    log_status = response2[0]

    if camera == "BOTTOM" and image_type == "RAW":
        target_count = int(log_status.num_bottom)
    elif camera == "TOP" and image_type == "RAW":
        target_count = int(log_status.num_top)
    elif camera == "BOTTOM" and image_type == "JPEG":
        target_count = int(log_status.num_jpg_bottom)
    elif camera == "TOP" and image_type == "JPEG":
        target_count = int(log_status.num_jpg_top)
    else:
        ValueError()

    if target_count == db_count:
        print("\tskipping insertion")
        return True

    return False


if __name__ == "__main__":
    # FIXME handle the case that frame does not exist explicitely
    log_root_path = os.environ.get("VAT_LOG_ROOT")
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    existing_data = client.logs.list()

    def myfunc(log):
        return log.log_path

    for log in sorted(existing_data, key=myfunc, reverse=False):
        log_path = Path(log_root_path) / log.log_path

        # TODO could we just switch game_logs with extracted in the paths?
        robot_foldername = log_path.parent.name
        game_folder = log_path.parent.parent.parent.name
        extracted_path = log_path.parent.parent.parent / "extracted" / robot_foldername

        bottom_path = extracted_path / "log_bottom"
        top_path = extracted_path / "log_top"
        bottom_path_jpg = extracted_path / "log_bottom_jpg"
        top_path_jpg = extracted_path / "log_top_jpg"

        handle_insertion(bottom_path, log, camera="BOTTOM", image_type="RAW")
        handle_insertion(top_path, log, camera="TOP", image_type="RAW")
        handle_insertion(bottom_path_jpg, log, camera="BOTTOM", image_type="JPEG")
        handle_insertion(top_path_jpg, log, camera="TOP", image_type="JPEG")
