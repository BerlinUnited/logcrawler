from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.log import Parser
import os
from vaapi.client import Vaapi
from tqdm import tqdm
import argparse


def is_done_motion(log_id):
    # get the log status - showing how many entries per representation there should be
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log=log_id)
        if len(response) == 0:
            return False
        log_status = response[0]
    except Exception as e:
        print(e)
    
    if not log_status.num_motion_frames or int(log_status.num_motion_frames) == 0:
        print("\tWARNING: first calculate the number of cognitions frames and put it in the db")
        quit()

    # TODO maybe add sanity check about too many frames in db
    response = client.motionframe.get_frame_count(log=log_id)
    print(response)
    if int(log_status.num_motion_frames) == int(response["count"]):
        return True
    else:
        return False


def parse_motion_log(log):
    sensor_log_path = Path(log_root_path) / log.sensor_log_path

    my_parser = Parser()
    game_log = LogReader(str(sensor_log_path), my_parser)

    frame_array = list()
    for idx, frame in enumerate(tqdm(game_log)):
        # stop parsing log if FrameInfo is missing
        try:
            frame_number = frame['FrameInfo'].frameNumber
            frame_time = frame['FrameInfo'].time

        except Exception as e:
            print(f"FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one")
            #print(f"last frame number was {frame_array[-1]['frame_number']}") # FIXME does not work if its the first frame or every 100th
            break
        
        json_obj = {
            "log":log.id, 
            "frame_number":frame_number,
            "frame_time": frame_time,
        }
        frame_array.append(json_obj)

        if idx % 100 == 0:
            try:
                response = client.motionframe.bulk_create(
                    frame_list=frame_array
                )
                frame_array.clear()
            except Exception as e:
                print(f"error inputing the data for {sensor_log_path}")
                print(e)
                quit()

    # handle the last frames
    # just upload whatever is in the array. There will be old data but that does not matter, it will be filtered out on insertion
    try:
        response = client.motionframe.bulk_create(
            frame_list=frame_array
        )
    except Exception as e:
        print(f"error inputing the data {sensor_log_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true", default=False)
    args = parser.parse_args()

    log_root_path = os.environ.get("VAT_LOG_ROOT")
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    existing_data = client.logs.list()

    def sort_key_fn(data):
        return data.log_path

    for log in sorted(existing_data, key=sort_key_fn, reverse=True):
        sensor_log_path = Path(log_root_path) / log.sensor_log_path

        print(f"{log.id}: {sensor_log_path}")
        if not is_done_motion(log.id) or args.force:
            parse_motion_log(log)
