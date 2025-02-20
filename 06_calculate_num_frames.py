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

        print("log_path: ", log_path)
        
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
                continue
            
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
        quit()

        # TODO figure out how we should handle adding additional representations?
        # NOTE when we use create above we have to use update for sensor log,
        motion_status_dict = {
            'FrameInfo': 0,
            'IMUData': 0,
            'FSRData': 0,
            'ButtonData': 0,
            'SensorJointData': 0,
            'AccelerometerData': 0,
            'InertialSensorData': 0,
            'MotionStatus': 0,
            'MotorJointData':0,
            'GyrometerData': 0,
        }

        new_motion_status_dict = is_done_motion(log_id, motion_status_dict)
        if not args.force and len(new_motion_status_dict) == 0:
            print("\twe already calculated number of full sensor frames for this log")
        else:
            if args.force:
                new_motion_status_dict = motion_status_dict
            my_parser = Parser()
            game_log = LogReader(str(sensor_log_path), my_parser)
            for idx, frame in enumerate(tqdm(game_log)):
                # stop parsing log if FrameInfo is missing
                try:
                    frame_number = frame['FrameInfo'].frameNumber
                except Exception as e:
                    print(f"FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one")
                    continue
                for repr in new_motion_status_dict:
                    try:
                        data = MessageToDict(frame[repr])
                        new_motion_status_dict[repr] += 1
                    except AttributeError:
                        # TODO only print something when in debug mode
                        #print("skip frame because representation is not present")
                        continue
                    except Exception as e:
                        print(f"error parsing {repr} in log {log_path} at frame {idx}")
                        print({e})

            try:
                if "FrameInfo" in new_motion_status_dict:
                    new_motion_status_dict['num_motion_frames'] = new_motion_status_dict.pop('FrameInfo')
                print(new_motion_status_dict)
                response = client.log_status.update(
                log_id=log_id, 
                **new_motion_status_dict
                )
            except Exception as e:
                print(f"\terror inputing the data {log_path}")
                print(e)
                quit()
