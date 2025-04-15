from pathlib import Path
import log_crawler
from google.protobuf.json_format import MessageToDict
from naoth.log import Parser
import os
from vaapi.client import Vaapi
import argparse


def input_frames_done(log_id):
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
        print("\tWARNING: first calculate the number of cognition frames and put it in the db")
        quit()

    response = client.cognitionframe.get_frame_count(log=log_id)
    if int(log_status.FrameInfo) == int(response["count"]):
        return True
    elif int(response["count"]) > int(log_status.FrameInfo):
        # rust based calculation for num frames stops if one broken representation is in the last frame
        print("ERROR: there are more frames in the database than they should be")
        print(f"Run logstatus calculation again for log {log_id} or make sure the end of the log is calculated the same way")
        quit()
    else:
        return False

def input_representation_done(representation_list):
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
    if not log_status.FrameInfo or int(log_status.FrameInfo) == 0:
        print("\tWARNING: first calculate the number of motion frames and put it in the db")
        quit()

    new_list = list()
    for repr in representation_list:
        # if no entry for a given representation is present this will throw an error
        try:
            # query the motion representation and check how many frames with a given representations are there
            model = getattr(client, repr.lower())
            num_repr_frames=model.get_repr_count(log=log.id)["count"]

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


def input_frames(crawler, parser):
    parsed_messages = list()
    frames = crawler.get_unparsed_representation_list("FrameInfo")
    for idx, (k, data) in enumerate(frames.items()):
        message = parser.parse("FrameInfo", bytes(data))

        json_obj = {
            "log":log.id, 
            "frame_number": message.frameNumber,
            "frame_time": message.time,
        }
        parsed_messages.append(json_obj)

        if idx % 1000 == 0:
            try:
                response = client.cognitionframe.bulk_create(
                    frame_list=parsed_messages
                )
                parsed_messages.clear()
            except Exception as e:
                print(f"error inputing the data for {log_path}")
                print(e)
                quit()
    
    # handle the last frames
    # just upload whatever is in the array. There will be old data but that does not matter, it will be filtered out on insertion
    try:
        response = client.cognitionframe.bulk_create(
            frame_list=parsed_messages
        )
    except Exception as e:
        print(f"error inputing the data {log_path}")


def input_representation_data(log, crawler, my_parser, representation_list):
    # get list of frames  for this log
    frames = client.cognitionframe.list(log=log.id)
    # Create a dictionary mapping frame_number to id
    frame_to_id = {frame.frame_number: frame.id for frame in frames}

    def get_id_by_frame_number(target_frame_number):
            return frame_to_id.get(target_frame_number, None)
    
    for repr_name in representation_list:
        repr_dict = crawler.get_unparsed_representation_list(repr_name)

        print(f"\tparse all {repr_name} messages in python")
        parsed_messages = list()
        for idx, (frame_number, data) in enumerate(repr_dict.items()):
            message = my_parser.parse(repr_name, bytes(data))
            
            message_dict = MessageToDict(message)

            json_obj = {
                "frame": get_id_by_frame_number(frame_number),
                "representation_data": message_dict
            }
            parsed_messages.append(json_obj)
            if idx % 600 == 0:
                try:
                    model = getattr(client, repr_name.lower())
                    model.bulk_create(repr_list=parsed_messages)
                    parsed_messages.clear()
                except Exception as e:
                    print(f"error inputing the data for {log_path}")
                    print(e)
                    quit()
        try:
            model = getattr(client, repr_name.lower())
            model.bulk_create(repr_list=parsed_messages)
        except Exception as e:
            print(f"error inputing the data {log_path}")

def get_cognition_representations(log):
    cog_repr = log.representation_list["cognition_representations"]
    if "ImageJPEGTop" in cog_repr: cog_repr.remove("ImageJPEGTop")
    if "ImageJPEG" in cog_repr: cog_repr.remove("ImageJPEG")
    if "ImageTop" in cog_repr: cog_repr.remove("ImageTop")
    if "Image" in cog_repr: cog_repr.remove("Image")
    # remove Frameinfo from the list, frameinfo is inserted as frames in db and not a seperate representation
    if "FrameInfo" in cog_repr: cog_repr.remove("FrameInfo")
    # remove BehaviorStateComplete and BehaviorStateSparse, this will be parsed seperately and in different models
    if "BehaviorStateComplete" in cog_repr: cog_repr.remove("BehaviorStateComplete")
    if "BehaviorStateSparse" in cog_repr: cog_repr.remove("BehaviorStateSparse")
    
    return cog_repr

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

    def sort_key_fn(log):
        return log.id

    for log in sorted(existing_data, key=sort_key_fn, reverse=True):
        log_path = Path(log_root_path) / log.log_path

        print(f"{log.id}: {log_path}")

        # get 
        representation_list = get_cognition_representations(log)

        if input_frames_done(log.id) and not args.force:
            new_representation_list = input_representation_done(representation_list)
            if len(new_representation_list) == 0:
                print("\tall required representations are already inserted, will continue with the next log")
                continue
        
        my_parser = Parser()
        my_parser.register("GoalPerceptTop", "GoalPercept")
        my_parser.register("FieldPerceptTop", "FieldPercept")
        my_parser.register("BallCandidatesTop", "BallCandidates")
        crawler = log_crawler.LogCrawler(str(log_path))
        
        if args.force:
            new_representation_list = representation_list

        if not input_frames_done(log.id) or args.force:
             input_frames(crawler, my_parser)

        if len(new_representation_list) != 0 or args.force:
            input_representation_data(log, crawler, my_parser, new_representation_list)
