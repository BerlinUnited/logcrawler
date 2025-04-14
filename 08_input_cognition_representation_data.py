from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.log import Parser
from google.protobuf.json_format import MessageToDict
import argparse
import os
from tqdm import tqdm
from vaapi.client import Vaapi


def is_input_done(representation_list):
    # get the log status - showing how many entries per representation there should be
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log=log.id)
        if len(response) == 0:
            return False
        log_status = response[0]
    except Exception as e:
        print(e)

    # check if number of frames were calculated already
    num_cognition_frames = log_status.FrameInfo
    if not num_cognition_frames or int(num_cognition_frames) == 0:
        print("\tWARNING: first calculate the number of cognitions frames and put it in the db")
        quit()

    new_list = list()
    for repr in representation_list:
        # if no entry for a given representation is present this will throw an error
        try:
            # query the cognition representation and check how many frames with a given representations are there
            model = getattr(client, repr.lower())
            num_repr_frames=model.get_repr_count(log=log_id)["count"]

            print(f"\t{repr} inserted frames: {num_repr_frames}/{getattr(log_status, repr)}")
            if int(getattr(log_status, repr)) != int(num_repr_frames):
                new_list.append(repr)
        except Exception as e:
            print(e)
            new_list.append(repr)

    if len(new_list) > 0:
        print("\tneed to run insertion again")
        print(f"{new_list}")
    return new_list
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true", default=False)
    args = parser.parse_args()

    log_root_path = os.environ.get("VAT_LOG_ROOT")
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    # get all logs
    existing_data = client.logs.list()

    def sort_key_fn(data):
        return data.log_path

    for log in sorted(existing_data, key=sort_key_fn, reverse=True):
        log_id = log.id

        log_path = Path(log_root_path) / log.log_path
        print(f"{log.id}: {log.log_path}")

        # representations that we want to put in the database if they exist in the log
        # NOTE is done would fail if frameinfo is here
        # FIXME load all representation from file or log model
        representation_list = [
            "BallModel",
            "BallCandidates",
            "BallCandidatesTop",
            "CameraMatrix",
            "CameraMatrixTop",
            "OdometryData",
            "FieldPercept",
            "FieldPerceptTop",
            "GoalPercept",
            "GoalPerceptTop",
            "MultiBallPercept",
            "RansacLinePercept", 
            "ShortLinePercept",
            "ScanLineEdgelPercept",
            "ScanLineEdgelPerceptTop",
            "RansacCirclePercept2018"
        ]
        
        # check if we need to insert this log
        new_representation_list = is_input_done(representation_list)
        if not args.force and len(new_representation_list) == 0:
            print("\tall required representations are already inserted, will continue with the next log")
            continue
        if args.force:
            new_representation_list = representation_list

        my_parser = Parser()
        my_parser.register("ImageJPEG"   , "Image")
        my_parser.register("ImageJPEGTop", "Image")
        my_parser.register("GoalPerceptTop", "GoalPercept")
        my_parser.register("FieldPerceptTop", "FieldPercept")
        my_parser.register("BallCandidatesTop", "BallCandidates")

        # get list of frames  for this log
        frames = client.cognitionframe.list(log=log.id)
        # Create a dictionary mapping frame_number to id
        frame_to_id = {frame.frame_number: frame.id for frame in frames}

        def get_id_by_frame_number(target_frame_number):
            return frame_to_id.get(target_frame_number, None)

        game_log = LogReader(str(log_path), my_parser)

        repr_lists = {}
        for idx, frame in enumerate(tqdm(game_log, desc=f"Parsing frame", leave=True)):
            for repr_name in frame.get_names():
                if not repr_name in new_representation_list:
                    continue
                
                # try accessing framenumber directly because we can have the situation where the framenumber is missing in the
                # last frame, also we don't want to parse other representations if frame number is missing
                try:
                    frame_number = frame['FrameInfo'].frameNumber
                except Exception as e:
                    print(f"FrameInfo not found in current frame - will not parse any other representation from this frame")
                    break

                try:
                    message_dict = MessageToDict(frame[repr_name])
                    # drop binary data from BallCandidates
                    if repr_name in ["BallCandidates", "BallCandidatesTop"]:
                        for patch in message_dict['patches']:
                            del patch['data']
                            del patch['type']

                except AttributeError:
                    #print("skip frame because representation is not present")
                    continue
                except Exception as e:
                    print(repr_name)
                    print(f"error parsing the log {log_path}")
                    print({e})
                    quit()

                # FIXME fix the backend to also handle normal create function
                json_obj = {
                    "frame": get_id_by_frame_number(frame_number), 
                    "representation_data": message_dict
                }
                # If the repr_name key doesn't exist in the dictionary, create a new list for it
                if repr_name not in repr_lists:
                    repr_lists[repr_name] = []

                # Append the json_obj to the appropriate list
                repr_lists[repr_name].append(json_obj)

            if idx % 250 == 0:
                for k,v in repr_lists.items():
                    try:
                        model = getattr(client, k.lower())
                        model.bulk_create(repr_list=v)
                        v.clear()
                    except Exception as e:
                        print(f"error inputing the data {log_path}")
                        print(e)
                        quit()
        # handle the last frames
        # just upload whatever is in the array. There will be old data but that does not matter, it will be filtered out on insertion
        for k,v in repr_lists.items():
            try:
                model = getattr(client, k.lower())
                model.bulk_create(repr_list=v)
            except Exception as e:
                print(f"error inputing the data {log_path}")
                print(e)
                quit()
