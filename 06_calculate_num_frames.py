from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.log import Parser
import os
from google.protobuf.json_format import MessageToDict
from vaapi.client import Vaapi
from tqdm import tqdm
import argparse

def is_done(log_id, status_dict):
    # TODO get log_status representation here and check each field.
    new_dict = status_dict.copy()
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log_id=log_id)
        if len(response) == 0:
            return status_dict
        log_status = response[0]

        for k,v in status_dict.items():
            if k == "FrameInfo":
                field_value = getattr(log_status, "num_cognition_frames")
            else:
                field_value = getattr(log_status, k)
            
            if field_value == None:
                print(f"\tdid not find a value for repr {k}")
            else:
                new_dict.pop(k)
        return new_dict
    # TODO would be nice to handle the vaapi API error here explicitely
    except Exception as e:
        print("error", e)
        quit()
        return status_dict

def is_done_motion(log_id, status_dict):
    # TODO get log_status representation here and check each field.
    new_dict = status_dict.copy()
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log_id=log_id)
        if len(response) == 0:
            return status_dict
        log_status = response[0]

        for k,v in status_dict.items():
            if k == "FrameInfo":
                field_value = getattr(log_status, "num_motion_frames")
            else:
                field_value = getattr(log_status, k)
            
            if field_value == None:
                print(f"\tdid not find a value for repr {k}")
            else:
                new_dict.pop(k)
        return new_dict
    # TODO would be nice to handle the vaapi API error here explicitely
    except Exception as e:
        print("error", e)
        quit()
        return status_dict


def parse_cognition_log(log_path):
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
            break
        
        json_obj = {
            "log_id":log_id, 
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
        print(response)
    except Exception as e:
        print(f"error inputing the data {log_path}")


def parse_motion_log(sensor_log_path):
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
            "log_id":log_id, 
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
                print(f"error inputing the data for {log_path}")
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
        print(f"error inputing the data {log_path}")

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

    for log_data in sorted(existing_data, key=sort_key_fn, reverse=True):
        log_id = log_data.id
        log_path = Path(log_root_path) / log_data.log_path
        sensor_log_path = Path(log_root_path) / log_data.sensor_log_path

        # FIXME add useful is done check here
        print("log_path: ", log_path)
        parse_cognition_log(log_path)
        
        # FIXME add useful is done check here
        print("log_path: ", sensor_log_path)
        parse_motion_log(sensor_log_path)