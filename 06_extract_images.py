import os
from naoth.log import Reader as LogReader
from naoth.log import Parser
from pathlib import Path
from tqdm import tqdm
import numpy as np
import io
import subprocess
from PIL import PngImagePlugin
from PIL import Image as PIL_Image
from vaapi.client import Vaapi

"""
TODO: check if images are corrupted
TODO: make force work like this:
- export image as temp name and only if not corrupted rename it to new name and overwrite the old file with this
TODO: build checker for corrupted images
"""


def is_done(log):
    # get the log status object for a given log_id
    response = client.log_status.list(log=log.id)

    if len(response) == 0:
        print("\tno log_status found for given log id")
        quit()
    
    log_status = response[0]
    total_images = int(log_status.Image or 0) + int(log_status.ImageTop or 0) + int(log_status.ImageJPEG or 0) + int(log_status.ImageJPEGTop or 0)
    if total_images == 0:
        print("\tCalculate the number of images for this log first")
        quit()

    # this has to check how many files are in the folder
    log_path = Path(log_root_path) / log.log_path
    extracted_path = str(log_path.parent).replace("game_logs", "extracted")

    jpg_bottom_path = Path(extracted_path) / "log_bottom_jpg"
    jpg_top_path = Path(extracted_path) / "log_top_jpg"
    bottom_path = Path(extracted_path) / "log_bottom"
    top_path = Path(extracted_path) / "log_top"

    num_bottom = subprocess.run(f"find {bottom_path} -maxdepth 1 -type f | wc -l", shell=True, capture_output=True, text=True).stdout.strip() if bottom_path.is_dir() else 0
    num_top = subprocess.run(f"find {top_path} -maxdepth 1 -type f | wc -l", shell=True, capture_output=True, text=True).stdout.strip() if top_path.is_dir() else 0
    num_jpg_bottom = subprocess.run(f"find {jpg_bottom_path} -maxdepth 1 -type f | wc -l", shell=True, capture_output=True, text=True).stdout.strip() if jpg_bottom_path.is_dir() else 0
    num_jpg_top = subprocess.run(f"find {jpg_top_path} -maxdepth 1  -type f | wc -l", shell=True, capture_output=True, text=True).stdout.strip() if jpg_top_path.is_dir() else 0

    # FIXME This will also extract images that are already extracted if the log status is not already calculated for this log
    if int(log_status.Image or 0) != int(num_bottom):
        print(f"Image Bottom: {log_status.Image or 0} != {num_bottom}")
        return False
    if int(log_status.ImageTop or 0) != int(num_top):
        print(f"Image Top: {log_status.ImageTop or 0} != {num_top}")
        return False
    if int(log_status.ImageJPEG or 0) != int(num_jpg_bottom):
        print(f"ImageJPEG: {log_status.ImageJPEG or 0} != {num_jpg_bottom}")
        return False
    if int(log_status.ImageJPEGTop or 0) != int(num_jpg_top):
        print(f"ImageJPEGTop: {log_status.ImageJPEGTop or 0} != {num_jpg_top}")
        return False
    
    return True


def save_images(frame):
    frame_number = format(frame.number, "07d")
    try:
        image_top = image_from_proto(frame["ImageTop"])
        cm_top = frame["CameraMatrixTop"]
        image_top = image_top.convert("RGB")
        save_image_to_png(
            frame_number, image_top, cm_top, out_top, cam_id=0, name=log.log_path
        )

    except KeyError:
        image_top = None
        cm_top = None

    try:
        image_top_jpeg = image_from_proto_jpeg(frame["ImageJPEGTop"])
        cm_top = frame["CameraMatrixTop"]
        image_top_jpeg = image_top_jpeg.convert("RGB")
        save_image_to_png(
            frame_number, image_top_jpeg, cm_top, out_top_jpg, cam_id=0, name=log.log_path
        )
    except KeyError:
        image_top_jpeg = None
        cm_top = None

    try:
        image_bottom = image_from_proto(frame["Image"])
        cm_bottom = frame["CameraMatrix"]
        image_bottom = image_bottom.convert("RGB")
        save_image_to_png(
            frame_number, image_bottom, cm_bottom, out_bottom, cam_id=1, name=log.log_path
        )
    except KeyError:
        image_bottom = None
        cm_bottom = None

    try:
        image_bottom_jpeg = image_from_proto_jpeg(frame["ImageJPEG"])
        cm_bottom = frame["CameraMatrix"]
        image_bottom_jpeg = image_bottom_jpeg.convert("RGB")
        save_image_to_png(
            frame_number, image_bottom_jpeg, cm_bottom, out_bottom_jpg, cam_id=1, name=log.log_path
        )
    except KeyError:
        image_bottom_jpeg = None
        cm_bottom = None



def image_from_proto(message):
    # read each channel of yuv422 separately
    yuv422 = np.frombuffer(message.data, dtype=np.uint8)
    y = yuv422[0::2]
    u = yuv422[1::4]
    v = yuv422[3::4]

    # convert from yuv422 to yuv888
    yuv888 = np.zeros(message.height * message.width * 3, dtype=np.uint8)

    yuv888[0::3] = y
    yuv888[1::6] = u
    yuv888[2::6] = v
    yuv888[4::6] = u
    yuv888[5::6] = v

    yuv888 = yuv888.reshape((message.height, message.width, 3))

    # convert the image to rgb and save it
    img = PIL_Image.frombytes(
        "YCbCr", (message.width, message.height), yuv888.tobytes()
    )
    return img


def image_from_proto_jpeg(message):
    
    # hack: 
    if message.format == message.JPEG:
        # unpack JPG
        img = PIL_Image.open(io.BytesIO(message.data))
    
        # HACK: for some reason the decoded image is inverted ...
        yuv422 = 255 - np.array(img, dtype=np.uint8)
        
        # flatten the image to get the same data formal like a usual yuv422
        yuv422 = yuv422.reshape(message.height * message.width * 2)
    else:
        # read each channel of yuv422 separately
        yuv422 = np.frombuffer(message.data, dtype=np.uint8)
    
    y = yuv422[0::2]
    u = yuv422[1::4]
    v = yuv422[3::4]

    # convert from yuv422 to yuv888
    yuv888 = np.zeros(message.height * message.width * 3, dtype=np.uint8)

    yuv888[0::3] = y
    yuv888[1::6] = u
    yuv888[2::6] = v
    yuv888[4::6] = u
    yuv888[5::6] = v

    yuv888 = yuv888.reshape((message.height, message.width, 3))
    
    # convert the image to rgb
    img = PIL_Image.frombytes('YCbCr', (message.width, message.height), yuv888.tobytes())
    
    return img


def save_image_to_png(j, img, cm, target_dir, cam_id, name):
    meta = PngImagePlugin.PngInfo()
    meta.add_text("Message", "rotation maxtrix is saved column wise")
    meta.add_text("logfile", str(name))
    meta.add_text("CameraID", str(cam_id))

    if cm:
        meta.add_text("t_x", str(cm.pose.translation.x))
        meta.add_text("t_y", str(cm.pose.translation.y))
        meta.add_text("t_z", str(cm.pose.translation.z))

        meta.add_text("r_11", str(cm.pose.rotation[0].x))
        meta.add_text("r_21", str(cm.pose.rotation[0].y))
        meta.add_text("r_31", str(cm.pose.rotation[0].z))

        meta.add_text("r_12", str(cm.pose.rotation[1].x))
        meta.add_text("r_22", str(cm.pose.rotation[1].y))
        meta.add_text("r_32", str(cm.pose.rotation[1].z))

        meta.add_text("r_13", str(cm.pose.rotation[2].x))
        meta.add_text("r_23", str(cm.pose.rotation[2].y))
        meta.add_text("r_33", str(cm.pose.rotation[2].z))
    filename = Path(target_dir) / (str(j) + ".png")
    img.save(filename, pnginfo=meta)


def get_log_path(log) -> str | None:
    """
    get either full path to game.log or combined.log
    """
    game_log_path = log_root_path / Path(log.log_path)
    combined_log_path = log_root_path / Path(log.combined_log_path)
    if combined_log_path.is_file():
        actual_log_path = combined_log_path
    elif game_log_path.is_file():
        actual_log_path = game_log_path
    else:
        actual_log_path = None
    return actual_log_path

def calculate_output_path(log_folder: str):
    # FIXME have a better detection if its experiment log or not
    """
    log_path_w_prefix = log_root_path / Path(log_folder)
    if Path(log_path_w_prefix).is_file():
        print("\tdetected experiment log")
        actual_log_folder = log_root_path / Path(log_folder).parent
        log = log_path_w_prefix

        extracted_folder = (
            Path(actual_log_folder) / Path("extracted") / Path(log_path_w_prefix).stem
        )
        output_folder_top = extracted_folder / Path("log_top")
        output_folder_bottom = extracted_folder / Path("log_bottom")
        output_folder_top_jpg = extracted_folder / Path("log_top_jpg")
        output_folder_bottom_jpg = extracted_folder / Path("log_bottom_jpg")

        print(f"\toutput folder will be {extracted_folder}")

    else:
    """
    print("\tdetected normal game log")
    actual_log_folder = Path(log_folder)
    

    extracted_folder = (
        Path(actual_log_folder).parent.parent
        / Path("extracted")
        / Path(actual_log_folder).name
    )

    output_folder_top = extracted_folder / Path("log_top")
    output_folder_bottom = extracted_folder / Path("log_bottom")
    output_folder_top_jpg = extracted_folder / Path("log_top_jpg")
    output_folder_bottom_jpg = extracted_folder / Path("log_bottom_jpg")

    return output_folder_top, output_folder_bottom, output_folder_top_jpg, output_folder_bottom_jpg


if __name__ == "__main__":
    # FIXME aborting this script can result in broken images being written
    # FIXME add a force flag so we can change wrong data
    log_root_path = os.environ.get("VAT_LOG_ROOT") 

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    existing_data = client.logs.list()

    def sort_key_fn(log):
        return log.log_path
    
    for log in sorted(existing_data, key=sort_key_fn, reverse=True):
        print(log.log_path)
        log_folder_path = Path(log_root_path) / Path(log.log_path).parent
        
        actual_log_path = get_log_path(log)
        # TODO why this check? That should never happen
        if actual_log_path is None:
            print("\tcouldnt find a valid log file")
            continue

        if is_done(log):
           print("\twe already counted all the images and put them in the db we assume that all images have been extracted")
           continue
        
        # get the combined_log path or the game.log path
        out_top, out_bottom, out_top_jpg, out_bottom_jpg = calculate_output_path(log_folder_path)
        

        out_top.mkdir(exist_ok=True, parents=True)
        out_bottom.mkdir(exist_ok=True, parents=True)
        out_top_jpg.mkdir(exist_ok=True, parents=True)
        out_bottom_jpg.mkdir(exist_ok=True, parents=True)

        my_parser = Parser()
        my_parser.register("ImageJPEG"   , "Image")
        my_parser.register("ImageJPEGTop", "Image")
        game_log = LogReader(str(actual_log_path), my_parser)

        for idx, frame in enumerate(tqdm(game_log)):
            try:
                frame_number = frame['FrameInfo'].frameNumber
                frame_time = frame['FrameInfo'].time
            except Exception as e:
                print(f"FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one")
                break
            
            save_images(frame)


        # HACK delete image folders if they are empty - this is just so that looking at the distracted folder is not confusing for humans
        # TODO we know beforehand if we have images or images jpeg in the log - we can just do it right the first time
        if not any(out_top_jpg.iterdir()):
            out_top_jpg.rmdir()
        if not any(out_bottom_jpg.iterdir()):
            out_bottom_jpg.rmdir()
        if not any(out_top.iterdir()):
            out_top.rmdir()
        if not any(out_bottom.iterdir()):
            out_bottom.rmdir()
        
        quit()