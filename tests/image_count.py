from pathlib import Path
import os
from tqdm import tqdm
from naoth.log import Reader as LogReader
from google.protobuf.json_format import MessageToDict
from naoth.log import Parser
from vaapi.client import Vaapi


def create_jpeg_image_log_dict(image_log):
    """
    Return a dictionary with frame numbers as key and image data as values.
    """

    myParser = Parser()
    myParser.register("ImageJPEG"   , "Image")
    myParser.register("ImageJPEGTop", "Image")

    reader = LogReader(image_log, parser=myParser)
    count1 = 0
    count2 = 0
    for frame in tqdm(reader):
        if "ImageJPEG" in frame.get_names():
            count1 += 1

        if "ImageJPEGTop" in frame.get_names():
           count2 += 1

    return count1


def count_images_jpeg_log(log_path):
    images_dict = create_jpeg_image_log_dict(log_path)
    print(images_dict)

def count_images_combined_log(combined_log_path):
    cognition_status_dict = {
        "Image": 0,
        "ImageTop": 0,
        "ImageJPEG": 0,
        "ImageJPEGTop": 0,
    }

    my_parser = Parser()
    my_parser.register("ImageTop", "Image")
    my_parser.register("ImageJPEG"   , "Image")
    my_parser.register("ImageJPEGTop", "Image")

    game_log = LogReader(str(combined_log_path), my_parser)
    for idx, frame in enumerate(tqdm(game_log)):
        # stop parsing log if FrameInfo is missing
        try:
            _ = frame['FrameInfo'].frameNumber
        except Exception as e:
            print("FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one")
            print(e)
            break
        for repr in cognition_status_dict:
            try:
                _ = MessageToDict(frame[repr])
                cognition_status_dict[repr] += 1
            except AttributeError:
                # TODO only print something when in debug mode
                #print("skip frame because representation is not present")
                continue
            except KeyError:
                # if image is not in frame
                continue
            except Exception as e:
                print(f"error parsing {repr} in log {combined_log_path} at frame {idx}")
                print({e})

    return cognition_status_dict

def main():
    log_root_path = os.environ.get("VAT_LOG_ROOT")
    
    existing_data = client.logs.list()

    def sort_key_fn(data):
        return data.log_path

    for log in sorted(existing_data, key=sort_key_fn, reverse=True):
        # TODO use combined log if its a file. -> it should always be a file if not experiment
        images_log_path = Path(log_root_path) / Path(log.log_path).parent / "images_jpeg.log"
        combined_log_path = Path(log_root_path) / log.combined_log_path

        # TODO count images from 
        jpeg_count = count_images_jpeg_log(images_log_path)
        quit()
        combined_jpeg_count = count_images_combined_log(combined_log_path)

        print("jpeg_count:", jpeg_count)
        print()
        print("combined_jpeg_count", combined_jpeg_count)
        # We only need to test one log
        quit()


if __name__ == "__main__":
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    main()