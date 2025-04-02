from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.log import Parser
import os
from google.protobuf.json_format import MessageToDict
from vaapi.client import Vaapi
from tqdm import tqdm
import argparse

def is_done(log_id):
    # get the log status - showing how many entries per representation there should be
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log=log_id)
        if len(response) == 0:
            return False
        log_status = response[0]
    except Exception as e:
        print(e)
    
    if not log_status.FrameInfo or int(log_status.FrameInfo) == 0:
        print("\tWARNING: first calculate the number of cognitions frames and put it in the db")
        quit()


    response = client.cognitionframe.get_frame_count(log=log_id)
    if int(log_status.FrameInfo) == int(response["count"]):
        return True
    else:
        print(log_status.FrameInfo, response["count"])
        return False


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


    response = client.motionframe.get_frame_count(log=log_id)
    if int(log_status.num_motion_frames) == int(response["count"]):
        return True
    else:
        return False


def parse_cognition_log(log_data):
    log_path = Path(log_root_path) / log_data.log_path

    my_parser = Parser()
    game_log = LogReader(str(log_path), my_parser)

    frame_array = list()
    for idx, frame in enumerate(tqdm(game_log)):
        # stop parsing log if FrameInfo is missing
        try:
            frame_number = frame['FrameInfo'].frameNumber
            frame_time = frame['FrameInfo'].time
        except Exception as e:
            print(f"FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one")
            print(f"last frame number was {frame_array[-1]['frame_number']}")
            break
        
        json_obj = {
            "log":log_data.id, 
            "frame_number":frame_number,
            "frame_time": frame_time,
        }
        frame_array.append(json_obj)

        if idx % 100 == 0:
            try:
                response = client.cognitionframe.bulk_create(
                    frame_list=frame_array
                )
                frame_array.clear()
            except Exception as e:
                print(f"error inputing the data for {log_path}")
                print(e)
                quit()
    
    # handle the last frames
    # just upload whatever is in the array. There will be old data but that does not matter, it will be filtered out on insertion
    try:
        response = client.cognitionframe.bulk_create(
            frame_list=frame_array
        )
    except Exception as e:
        print(f"error inputing the data {log_path}")


def parse_motion_log(log_data):
    sensor_log_path = Path(log_root_path) / log_data.sensor_log_path

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
            break
        
        json_obj = {
            "log":log_data.id, 
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
        print(response)
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

    for log_data in sorted(existing_data, key=sort_key_fn, reverse=False):
        print("log_path: ", log_data.log_path)
        if not is_done(log_data.id):
            parse_cognition_log(log_data)
        
        print("log_path: ", log_data.sensor_log_path)
        if not is_done_motion(log_data.id):
            parse_motion_log(log_data)
        quit()